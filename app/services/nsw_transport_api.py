import logging
import time
from datetime import datetime
from typing import Dict, Optional, Set

import requests
from cachetools import cached

from app.core.config import (MAX_REQUESTS_PER_SECOND,
                             NSW_TRANSPORT_BASE_API_URL, get_facility_url,
                             get_nsw_headers)
from app.services.cache_service import (carpark_ids_cache,
                                        carpark_locations_cache,
                                        no_update_carparks_cache)
from app.utils.time_utils import get_local_time, parse_message_date

logger = logging.getLogger(__name__)

# Global variables for rate limiting
request_count = 0
last_request_time = time.time()


def reset_request_counter():
    """
    The NSW Transport API has a throttle limit of 5 requests per second.
    Reset the request counter if we're in a new second
    """

    # Access global variables for request tracking
    global request_count, last_request_time

    # Get current Unix timestamp
    current_time = time.time()

    # Check if we've moved into a new second by comparing integer timestamps
    # This resets the counter at the start of each new second
    if int(current_time) > int(last_request_time):
        # Reset request counter
        request_count = 0
        # Update last request time
        last_request_time = current_time


def wait_for_next_second():
    """
    Wait until the start of the next second
    """

    current_time = time.time()
    wait_time = 1.0 - (current_time - int(current_time))
    if wait_time > 0:
        time.sleep(wait_time)


def make_api_request(url, headers) -> dict | None:
    """
    Make an API request with the throttle limiting
    (Because the NSW API has a throttle limit of 5 requests per second)

    Parameters:
        url (str): The URL to make the request to
        headers (dict): Headers to include in the request

    Returns:
        requests.Response: The response object if successful
        None: If the request fails
    """

    global request_count

    # Reset the request_count as 0 if we're in a new second
    reset_request_counter()

    # If we've hit the throttle limit (5 requests per second)
    # wait for next second and reset request_count
    if request_count >= MAX_REQUESTS_PER_SECOND:
        # wait the left time in one second
        wait_for_next_second()
        # reset request_count as 0
        reset_request_counter()

    try:
        # Make the API request and increase request_count
        response = requests.get(url, headers=headers, timeout=10)
        request_count += 1

        # Handle throttle limit exceeded (HTTP 429) by waiting and retrying
        if response.status_code == 429 or response.status_code == 403:
            wait_for_next_second()
            reset_request_counter()
            response = requests.get(url, headers=headers, timeout=10)
            request_count += 1

        # do not return the response if the request fails
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        # 404 error, cannot find the resources
        logger.error(f"API request failed: {e}")

        return None


@cached(carpark_ids_cache)
def get_all_carpark_ids() -> Optional[Dict]:
    """
    Query all carparks information from the NSW Transport API.

    Returns:
        dict: Dictionary mapping facility IDs to facility names,
              or None if request fails
        API response example:
            {
                "facility_id": "facility_name"
                ...
            }
    """
    return make_api_request(url=NSW_TRANSPORT_BASE_API_URL, headers=get_nsw_headers())


def get_carpark_details(facility_id: str, retry_count: int = 3) -> Optional[Dict]:
    """
    Get carpark details for a given facility ID with retry logic

    Parameters:
        facility_id (str): The ID of the carpark facility to query
        retry_count (int, optional): Number of retry attempts if request fails.
                                   Defaults to 3.

    Returns:
        dict: JSON response containing carpark details if successful,
              None if all retries fail

        {
            "tsn":,
            "time":,
            "spots":,
            "zones":[
                {
                    "spots":,
                    "zone_id":,
                    "occupancy":{
                        "loop":,
                        "total":,
                        "monthlies":,
                        "open_gate":,
                        "transients":
                    },
                    "zone_name":,
                    "parent_zone_id":
                }
            ],
            "ParkID":,
            "location":{
                "suburb":,
                "address":,
                "latitude":,
                "longitude":
            },
            "occupancy":{
                "loop":,
                "total":,
                "monthlies":,
                "open_gate":,
                "transients":
            },
            "MessageDate":,
            "facility_id":,
            "facility_name":,
            "tfnsw_facility_id":
        }
    """

    for attempt in range(retry_count):
        if attempt > 0:
            logger.info(
                "Retry {}/{} for facility {}".format(
                    attempt, retry_count - 1, facility_id
                )
            )
        response = make_api_request(
            url=get_facility_url(facility_id), headers=get_nsw_headers()
        )
        if response:
            logger.info("API request successful for facility {}".format(facility_id))
            return response
    return None


def is_carpark_no_update(
    details: Dict, current_time: datetime, no_update_hours: int = 24
) -> bool:
    """
    Determine if a carpark is considered no update.

    Parameters:
        details (dict): The carpark details
        current_time (datetime): The current time
        no_update_hours (int): The number of hours after which the carpark is
                              considered no update

    Returns:
        bool: True if the carpark is considered no update, False otherwise
    """

    msg_date_str = details.get("MessageDate")
    if not msg_date_str:
        return True

    msg_date = parse_message_date(msg_date_str)
    if not msg_date:
        return True

    age_hours = (current_time - msg_date).total_seconds() / 3600

    return age_hours > no_update_hours


def fetch_no_update_carparks(carpark_ids: Dict, current_time: datetime) -> Set[str]:
    """
    Check all carparks and return the ones that have no update.

    Parameters:
        carpark_ids (dict): Dictionary mapping facility IDs to facility names
        current_time (datetime): The current time

    Returns:
        Set[str]: Set of facility IDs that are considered no-update
    """
    no_update_set = set()
    for facility_id, _ in carpark_ids.items():
        logger.debug("Checking facility {}...".format(facility_id))
        details = get_carpark_details(facility_id)
        if not details or is_carpark_no_update(details, current_time):
            no_update_set.add(str(facility_id))
            logger.info("Facility {} is no-update".format(facility_id))
    return no_update_set


@cached(no_update_carparks_cache)
def get_no_update_carparks() -> Set[str]:
    """
    Get carparks that haven't updated within hours, using in-memory cache.

    Returns:
        Set[str]: Set of facility IDs that are considered no-update
    """
    carpark_ids = get_all_carpark_ids()
    if not carpark_ids:
        return set()
    return fetch_no_update_carparks(carpark_ids, get_local_time())


@cached(carpark_locations_cache)
def get_carpark_locations() -> Optional[Dict]:
    """
    Get all carparks information from the NSW Transport API.

    Returns:
        dict: Dictionary containing list of carparks with their details
        API response example:
            {
                "carparks": [
                    {
                        "facility_id": str,
                        "name": str,
                        "location": {
                            "latitude": float,
                            "longitude": float
                        }
                    }
                ]
            }
    """

    # Get mapping of facility IDs to names
    carpark_ids = get_all_carpark_ids()
    if not carpark_ids:
        return None

    # Get no-update carparks once
    no_update_carparks = get_no_update_carparks()
    carparks_list = []

    for facility_id, name in carpark_ids.items():
        # Skip if carpark is known to be no-update
        if facility_id in no_update_carparks:
            continue

        details = get_carpark_details(facility_id)
        if not details:
            continue

        location = details.get("location", {})
        if not location:
            continue

        try:
            carpark = {
                "facility_id": facility_id,
                "name": name,
                "location": {
                    "latitude": float(location.get("latitude")),
                    "longitude": float(location.get("longitude")),
                },
            }
            carparks_list.append(carpark)
        except (TypeError, ValueError) as e:
            logger.error("Error processing carpark {}: {}".format(facility_id, e))
            continue

    return {"carparks": carparks_list}


def available_status(spots: int, occupancy: int) -> str:
    """
    Get the available status of a carpark

    Parameters:
        spots (int): The total number of spots
        occupancy (int): The number of occupied spots

    Returns:
        str: The available status of the carpark
        API response example:
            "Full"
            "Almost Full"
            "Available"
    """
    available_spots = spots - occupancy
    if available_spots <= 0:
        return "Full"
    elif available_spots <= spots * 0.2:
        return "Almost Full"
    else:
        return "Available"

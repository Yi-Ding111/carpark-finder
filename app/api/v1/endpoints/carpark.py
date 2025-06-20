import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.core.security import verify_api_key
from app.models.schemas import Carpark, CarparkDetail
from app.services.nsw_transport_api import (
    available_status,
    get_carpark_details,
    get_carpark_locations,
    get_no_update_carparks,
)
from app.utils.distance import haversine_distance
from app.utils.time_utils import parse_message_date

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/nearby", response_model=List[Carpark])
async def get_nearby_carparks(
    lat: float = Query(..., description="Latitude of the search point"),
    lng: float = Query(..., description="Longitude of the search point"),
    radius_km: float = Query(10, description="Search radius in kilometers", ge=0),
    api_key: str = Depends(verify_api_key),
):
    """
    Get a list of carparks within the specified radius from a given location.

    Parameters:
        lat (float): Latitude of the search point
        lng (float): Longitude of the search point
        radius_km (float): Search radius in kilometers, default is 10km
        api_key (str): API key for authentication

    Returns:
        List[Carpark]: List of carpark objects within the radius
    """
    try:
        data = get_carpark_locations()
        if not data:
            return []

        carparks = data.get("carparks", [])
        if not isinstance(carparks, list):
            logger.warning("Unexpected structure: carparks is not a list")
            return []

        nearby_carparks = []
        for carpark in carparks:
            try:
                carpark_lat = float(carpark.get("location", {}).get("latitude"))
                carpark_lon = float(carpark.get("location", {}).get("longitude"))

                distance = haversine_distance(lat, lng, carpark_lat, carpark_lon)

                if distance <= radius_km:
                    nearby_carparks.append(
                        Carpark(
                            facility_id=carpark.get("facility_id"),
                            name=carpark.get("name", "Unknown"),
                            distance_km=round(distance, 2),
                        )
                    )

            except (TypeError, ValueError) as e:
                logger.error("Error processing carpark {}: {}".format(carpark.get("facility_id"), e))
                continue

        return sorted(nearby_carparks, key=lambda x: x.distance_km)

    except Exception as e:
        logger.error("Error in get_nearby_carparks: {}".format(str(e)))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{facility_id}", response_model=CarparkDetail)
async def get_carpark_available_details(
    facility_id: str = Path(..., pattern=r"^\d+$"),
    api_key: str = Depends(verify_api_key),
):
    """
    Get detailed information about a specific carpark

    Args:
        facility_id (str): ID of the carpark facility
        api_key (str): API key for authentication

    Returns:
        dict: Carpark details including total spots, available spots,
              status and last update
    """
    # Check if the carpark is no-update
    no_update_set = get_no_update_carparks()
    if facility_id in no_update_set:
        return CarparkDetail(
            facility_id=facility_id,
            name="Unknown",
            total_spots=0,
            available_spots=0,
            status="No Data Available",
            timestamp=None,
        )

    # Get the carpark details
    details = get_carpark_details(facility_id)

    # If the carpark is not found, return a 404 error
    if not details:
        raise HTTPException(status_code=404, detail="Carpark with ID {} not found".format(facility_id))

    # Get the total spots and occupancy
    try:
        total_spots = int(details.get("spots", 0))
        occupancy = int(details.get("occupancy", {}).get("total", 0))
    except (TypeError, ValueError) as e:
        logger.error("Invalid spot or occupancy data for carpark {}: {}".format(facility_id, e))
        raise HTTPException(status_code=500, detail="Internal server error")

    # Get the timestamp
    msg_date = details.get("MessageDate")
    timestamp = None
    if msg_date:
        try:
            timestamp = parse_message_date(msg_date)
        except Exception as e:
            logger.warning("Failed to parse MessageDate: {} ({})".format(msg_date, e))

    available_spots = max(total_spots - occupancy, 0)
    status = available_status(total_spots, occupancy)

    return CarparkDetail(
        facility_id=facility_id,
        name=details.get("facility_name", "Unknown"),
        total_spots=total_spots,
        available_spots=available_spots,
        status=status,
        timestamp=timestamp,
    )

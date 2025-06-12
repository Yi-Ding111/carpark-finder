import pytest
from datetime import datetime, timezone
from pytz import timezone as pytz_timezone
from app.utils.distance import haversine_distance
from app.utils.time_utils import parse_message_date, get_local_time
from app.services.nsw_transport_api import available_status


def test_haversine_distance():
    """
    Test the haversine distance calculation.

    Test the distance between Parramatta and UNSW.
    """
    #
    parramatta_lat, parramatta_lon = -33.8150, 151.0011
    unsw_lat, unsw_lon = -33.9173, 151.2313

    distance = haversine_distance(parramatta_lat, parramatta_lon, unsw_lat, unsw_lon)

    assert isinstance(distance, float)

    assert 20 <= distance <= 25


def test_get_local_time():
    """
    Test the get_local_time function.

    This function is used to get the current time in the local timezone.
    """

    result = get_local_time()
    
    # check if the result is a datetime object
    assert isinstance(result, datetime)

    # check if the timezone is Australia/Sydney
    assert result.tzinfo is not None
    assert result.tzinfo.zone == "Australia/Sydney"


def test_parse_message_date(mock_sydney_local_time):
    """
    Test parse_message_date function.

    This function is used to parse the message date string (MessageDate) to a datetime object.
    """
    result = parse_message_date(mock_sydney_local_time)
    
    assert isinstance(result, datetime)
    assert result.strftime("%Y-%m-%d %H:%M:%S") == "2025-06-12 11:08:35"
    # check if the timezone is Australia/Sydney
    assert result.tzinfo is not None
    assert result.tzinfo.zone == "Australia/Sydney"


def test_available_status():
    """
    Test carpark status calculation.
    """
    # Test different occupancy scenarios
    assert available_status(100, 0) == "Available"
    assert available_status(100, 80) == "Almost Full"
    assert available_status(100, 95) == "Full"
    assert available_status(100, 100) == "Full"

    # edge cases
    assert available_status(0, 0) == "No Data Available"
    assert available_status(100, -1) == "No Data Available"
    assert available_status(-1, 0) == "No Data Available"

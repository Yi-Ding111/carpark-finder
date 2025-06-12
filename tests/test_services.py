# test the nsw_transport_api.py
# check if the functions could do rate limiting
# test the cache_service.py

import pytest
import time
from unittest.mock import patch
from app.services.nsw_transport_api import (
    available_status,
    get_carpark_details,
    get_carpark_locations,
    get_no_update_carparks,
    reset_request_counter,
    wait_for_next_second,
    make_api_request,
    get_all_carpark_ids,
)


def test_reset_request_counter():
    """
    Test the reset_request_counter function.
    
    This test verifies that the request counter is reset when enough time has passed.
    """
    # Set initial values
    reset_request_counter.request_count = 5
    reset_request_counter.last_request_time = 100.0
    
    # Mock time.time() to return a time in the next second
    with patch("time.time", return_value=101.1):
        reset_request_counter()
    print(reset_request_counter.request_count)
    print(reset_request_counter.last_request_time)
    print(reset_request_counter.current_time)
    # Counter should be reset
    assert reset_request_counter.request_count == 0
    assert reset_request_counter.last_request_time == 101.1

# def test_reset_request_counter_same_second():
#     """
#     Test that the counter is not reset when in the same second.
#     """
#     # Set initial values
#     reset_request_counter.request_count = 5
#     reset_request_counter.last_request_time = 100.0
    
#     # Mock time.time() to return a time in the same second
#     with patch("time.time", return_value=100.5):
#         reset_request_counter()
    
#     # Counter should not be reset
#     assert reset_request_counter.request_count == 5
#     assert reset_request_counter.last_request_time == 100.0

# def test_wait_for_next_second():
#     """
#     Test the wait_for_next_second function.
#     """
#     with patch("time.time", return_value=100.7), \
#          patch("time.sleep") as mock_sleep:
#         wait_for_next_second()
#         mock_sleep.assert_called_once_with(pytest.approx(0.3, abs=0.1))

# def test_make_api_request_success():
#     """
#     Test successful API request.
#     """
#     mock_response = {"test": "data"}
    
#     with patch("requests.get") as mock_get:
#         mock_get.return_value.status_code = 200
#         mock_get.return_value.json.return_value = mock_response
        
#         response = make_api_request("test_url", {"header": "value"})
        
#         assert response == mock_response
#         mock_get.assert_called_once()

# def test_make_api_request_rate_limit():
#     """
#     Test API request with rate limiting.
#     """
#     mock_response = {"test": "data"}
    
#     with patch("requests.get") as mock_get, \
#          patch("time.sleep") as mock_sleep:
        
#         # First request gets rate limited
#         mock_get.return_value.status_code = 429
#         mock_get.return_value.json.return_value = mock_response
        
#         response = make_api_request("test_url", {"header": "value"})
        
#         assert response == mock_response
#         assert mock_get.call_count == 2  # Initial request + retry
#         mock_sleep.assert_called_once()





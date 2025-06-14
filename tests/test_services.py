# test the nsw_transport_api.py
# check if the functions could do rate limiting
# check if the functions could cache the result
# check if the functions could handle the error
# check if the functions could get the correct result

import time
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import pytz
import requests

from app.core import config
from app.services import nsw_transport_api
from app.services.nsw_transport_api import (available_status,
                                            fetch_no_update_carparks,
                                            get_all_carpark_ids,
                                            get_carpark_locations,
                                            get_no_update_carparks,
                                            is_carpark_no_update)


def test_reset_request_counter():
    """
    Test the reset_request_counter function.
    This function is used to reset the request counter if we're in a new second.

    This test verifies that the request counter is reset when enough time has passed.
    (Because the request counter is a global variable, we need to use the nsw_transport_api module to access it.)
    """
    # mock the request_count to 5
    nsw_transport_api.request_count = 5
    # mock the last_request_time to 100.0
    nsw_transport_api.last_request_time = 100.0

    # mock the time.time() to 101.0
    with patch("app.services.nsw_transport_api.time.time", return_value=101.0):
        nsw_transport_api.reset_request_counter()

    # verify the request_count and last_request_time
    assert nsw_transport_api.request_count == 0
    assert nsw_transport_api.last_request_time == 101.0


def test_reset_request_counter_same_second():
    """
    Test the reset_request_counter function.

    This test verifies that the request counter is not reset when in the same second.
    (Because the request counter is a global variable, we need to use the nsw_transport_api module to access it.)
    """
    # mock the request_count to 5
    nsw_transport_api.request_count = 4
    # mock the last_request_time to 100.0
    nsw_transport_api.last_request_time = 100.0

    # Mock time.time() to return a time in the same second
    with patch("app.services.nsw_transport_api.time.time", return_value=100.5):
        nsw_transport_api.reset_request_counter()

    # Counter should not be reset
    assert nsw_transport_api.request_count == 4
    assert nsw_transport_api.last_request_time == 100.0


def test_wait_for_next_second_calls_sleep():
    """
    Test the wait_for_next_second function.

    This test verifies that the wait_for_next_second function calls the sleep function.
    """
    # mock the time.time() to 100.3
    fake_time = 100.3
    expected_sleep_time = 1.0 - (fake_time - int(fake_time))  # 0.7

    # mock the time.time() to 100.3
    with patch(
        "app.services.nsw_transport_api.time.time", return_value=fake_time
    ), patch("app.services.nsw_transport_api.time.sleep") as mock_sleep:

        nsw_transport_api.wait_for_next_second()

        # verify the sleep function is called once, and the parameter is 0.7 (approximately)
        mock_sleep.assert_called_once()
        # (args, kwargs)
        args, _ = mock_sleep.call_args
        assert pytest.approx(args[0], 0.001) == expected_sleep_time


def test_make_api_request_success(mock_url, mock_headers, mock_success_response):
    """
    Test the make_api_request function.

    This test verifies that the make_api_request function could make a successful request.
    If the make_api_request() does not correctly handle the result of response.json(), this test will fail.

    Parameters:
        mock_url: the mock url
        mock_headers: the mock headers
        mock_success_response: the mock success response
    """
    # mock the requests.get function
    # mock the get request to return the mock response
    # mock the reset_request_counter as null function,do nothing
    # mock the wait_for_next_second as null function,do nothing
    with patch(
        "app.services.nsw_transport_api.requests.get",
        return_value=mock_success_response,
    ), patch("app.services.nsw_transport_api.reset_request_counter"), patch(
        "app.services.nsw_transport_api.wait_for_next_second"
    ):

        result = nsw_transport_api.make_api_request(mock_url, mock_headers)

        # verify the result
        assert result == {"result": "ok"}


def test_make_api_request_rate_limit(mock_url, mock_headers, mock_success_response):
    """
    Test the make_api_request function.

    Test that make_api_request retries once on 429 Too Many Requests,
    then succeeds on the second attempt.

    Parameters:
        mock_url: the mock url
        mock_headers: the mock headers
        mock_success_response: the mock success response
    """
    # First mock response: 429 Too Many Requests
    mock_response_429 = MagicMock()
    mock_response_429.status_code = 429
    mock_response_429.raise_for_status.side_effect = None
    mock_response_429.json.return_value = {}

    # do the side effect, first return 429, then return 200
    with patch(
        "app.services.nsw_transport_api.requests.get",
        side_effect=[mock_response_429, mock_success_response],
    ), patch("app.services.nsw_transport_api.reset_request_counter"), patch(
        "app.services.nsw_transport_api.wait_for_next_second"
    ):

        result = nsw_transport_api.make_api_request(mock_url, mock_headers)

        assert result == {"result": "ok"}


def test_make_api_request_throttle_limit_and_reset(
    mock_url, mock_headers, mock_success_response
):
    """
    Test the make_api_request function.

    Test make_api_request when rate limit is hit (request_count >= MAX_REQUESTS_PER_SECOND).
    After reset and making a request, request_count should be 1.

    Parameters:
        mock_url: the mock url
        mock_headers: the mock headers
        mock_success_response: the mock success response
    """

    # mock the request_count to the max requests per second (5 requests per second)
    nsw_transport_api.request_count = config.MAX_REQUESTS_PER_SECOND
    # mock the last_request_time to the time 2 seconds ago
    nsw_transport_api.last_request_time = time.time() - 2

    # patch the requests.get function to return the mock response
    with patch(
        "app.services.nsw_transport_api.requests.get",
        return_value=mock_success_response,
    ):
        result = nsw_transport_api.make_api_request(mock_url, mock_headers)

        assert result == {"result": "ok"}
        assert nsw_transport_api.request_count == 1


def test_make_api_request_error_returns_none(mock_url, mock_headers):
    """
    Test the make_api_request function.

    Test make_api_request returns None when a request exception occurs.

    Parameters:
        mock_url: the mock url
        mock_headers: the mock headers
    """
    # mock the requests.get function to raise a RequestException
    with patch(
        "app.services.nsw_transport_api.requests.get",
        side_effect=requests.exceptions.RequestException("Network Error"),
    ):
        result = nsw_transport_api.make_api_request(mock_url, mock_headers)
        assert result is None


def test_get_all_carpark_ids_cache(mock_all_carparks_response):
    """
    Test the get_all_carpark_ids function.

    This test verifies that the get_all_carpark_ids function could cache the result.

    Parameters:
        mock_all_carparks_response: the mock all carpark ids response
    """
    # mock the make_api_request function to return the mock response
    with patch(
        "app.services.nsw_transport_api.make_api_request",
        return_value=mock_all_carparks_response,
    ) as mock_api:
        # first call: should call make_api_request
        result1 = get_all_carpark_ids()
        assert result1 == mock_all_carparks_response

        # second call: should hit the cache, and not call make_api_request
        result2 = get_all_carpark_ids()
        assert result2 == mock_all_carparks_response

        # verify the mock_api is called only once
        assert mock_api.call_count == 1


def test_get_carpark_details_success(mock_carpark_details, mock_url, mock_headers):
    """
    Test the get_carpark_details function.

    This test verifies that the get_carpark_details function could get the correct result.

    Parameters:
        mock_carpark_details: the mock carpark details
        mock_url: the mock url
        mock_headers: the mock headers
    """

    with patch(
        "app.services.nsw_transport_api.make_api_request",
        return_value=mock_carpark_details,
    ), patch(
        "app.services.nsw_transport_api.get_facility_url", return_value=mock_url
    ), patch(
        "app.services.nsw_transport_api.get_nsw_headers", return_value=mock_headers
    ):

        result = nsw_transport_api.get_carpark_details(
            mock_carpark_details["facility_id"]
        )

        assert result == mock_carpark_details


def test_get_carpark_details_retry_success(
    mock_carpark_details, mock_url, mock_headers
):
    """
    Test the get_carpark_details function.

    This test verifies that the get_carpark_details function could retry the request when the request fails.

    Parameters:
        mock_carpark_details: the mock carpark details
        mock_url: the mock url
        mock_headers: the mock headers
    """

    # First call returns None, second call returns response
    # mock the make_api_request function to return None, then return the mock response
    with patch(
        "app.services.nsw_transport_api.make_api_request",
        side_effect=[None, mock_carpark_details],
    ), patch(
        "app.services.nsw_transport_api.get_facility_url", return_value=mock_url
    ), patch(
        "app.services.nsw_transport_api.get_nsw_headers", return_value=mock_headers
    ):

        result = nsw_transport_api.get_carpark_details(
            mock_carpark_details["facility_id"], retry_count=3
        )

        assert result == mock_carpark_details


def test_get_carpark_details_all_fail(mock_url, mock_headers):
    """
    Test the get_carpark_details function.

    This test verifies that the get_carpark_details function could return None when all retries fail.

    Parameters:
        mock_url: the mock url
        mock_headers: the mock headers
    """
    with patch(
        "app.services.nsw_transport_api.make_api_request", return_value=None
    ), patch(
        "app.services.nsw_transport_api.get_facility_url", return_value=mock_url
    ), patch(
        "app.services.nsw_transport_api.get_nsw_headers", return_value=mock_headers
    ):

        result = nsw_transport_api.get_carpark_details("999", retry_count=3)

        assert result is None


def test_no_message_date(mock_sydney_local_time):
    """
    Test the is_carpark_no_update function.

    This test verifies that the is_carpark_no_update function could return True when the message date is not in the details.

    Parameters:
        mock_sydney_local_time: the mock sydney local time
    """
    assert (
        is_carpark_no_update({}, datetime.fromisoformat(mock_sydney_local_time)) is True
    )


def test_invalid_message_date(mock_sydney_local_time):
    """
    Test the is_carpark_no_update function.

    This test verifies that the is_carpark_no_update function could return True when the message date is invalid.
    """
    details = {"MessageDate": "invalid-date-format"}
    assert (
        is_carpark_no_update(details, datetime.fromisoformat(mock_sydney_local_time))
        is True
    )


def test_recent_update(mock_sydney_local_time, mock_carpark_details):
    """
    Test the is_carpark_no_update function.

    This test verifies that the is_carpark_no_update function could return False when the message date is recent.

    Parameters:
        mock_sydney_local_time: the mock sydney local time
        mock_carpark_details: the mock carpark details
    """
    # the format should follow the result from get_local_time()
    current_time = pytz.timezone("Australia/Sydney").localize(
        datetime.fromisoformat(mock_sydney_local_time)
    )
    assert (
        is_carpark_no_update(mock_carpark_details, current_time, no_update_hours=24)
        is False
    )


def test_fetch_no_update_carparks_all_stale(
    mock_all_carparks_response, mock_sydney_local_time, mock_carpark_details
):
    """
    Test the fetch_no_update_carparks function.

    This test verifies that the fetch_no_update_carparks function could return the correct result.
    All carpark should be returned.

    Parameters:
        mock_all_carparks_response: the mock all carpark ids response
        mock_sydney_local_time: the mock sydney local time
        mock_carpark_details: the mock carpark details
    """
    # the format should follow the result from get_local_time()
    current_time = pytz.timezone("Australia/Sydney").localize(
        datetime.fromisoformat(mock_sydney_local_time)
    )
    # the all_carpark_ids should be the keys of the mock_all_carparks_response
    all_carpark_ids = {id for id in mock_all_carparks_response.keys()}

    # is_carpark_no_update should return True for all carpark details
    # True result means the carpark is no update
    with patch(
        "app.services.nsw_transport_api.get_carpark_details",
        return_value=mock_carpark_details,
    ), patch("app.services.nsw_transport_api.is_carpark_no_update", return_value=True):

        result = fetch_no_update_carparks(mock_all_carparks_response, current_time)

        assert result == all_carpark_ids


def test_fetch_no_update_carparks_mixed(
    mock_all_carparks_response, mock_sydney_local_time
):
    """
    Test the fetch_no_update_carparks function.

    This test verifies that the fetch_no_update_carparks function could return the correct result.
    Both the recent and no-update carpark should be returned.

    Parameters:
        mock_all_carparks_response: the mock all carpark ids response
        mock_sydney_local_time: the mock sydney local time
    """

    # the format should follow the result from get_local_time()
    current_time = pytz.timezone("Australia/Sydney").localize(
        datetime.fromisoformat(mock_sydney_local_time)
    )
    # the all_carpark_ids should be the keys of the mock_all_carparks_response
    with patch("app.services.nsw_transport_api.get_carpark_details") as mock_get, patch(
        "app.services.nsw_transport_api.is_carpark_no_update"
    ) as mock_is_stale:

        # return the mock carpark details
        mock_get.side_effect = lambda fid: {"facility_id": fid}

        # only 222 is no-update
        mock_is_stale.side_effect = lambda details, _: details["facility_id"] == "222"

        result = fetch_no_update_carparks(mock_all_carparks_response, current_time)

        assert result == {"222"}
        assert mock_get.call_count == 3
        assert mock_is_stale.call_count == 3


def test_fetch_no_update_carparks_no_stale(
    mock_all_carparks_response, mock_sydney_local_time, mock_carpark_details
):
    """
    Test the fetch_no_update_carparks function.

    This test verifies that the fetch_no_update_carparks function could return the correct result.
    No carpark should be returned.

    Parameters:
        mock_all_carparks_response: the mock all carpark ids response
        mock_sydney_local_time: the mock sydney local time
        mock_carpark_details: the mock carpark details
    """
    # the format should follow the result from get_local_time()
    current_time = pytz.timezone("Australia/Sydney").localize(
        datetime.fromisoformat(mock_sydney_local_time)
    )

    # is_carpark_no_update should return False for all carpark details
    # False result means the carpark is all update
    with patch(
        "app.services.nsw_transport_api.get_carpark_details",
        return_value=mock_carpark_details,
    ), patch("app.services.nsw_transport_api.is_carpark_no_update", return_value=False):

        result = fetch_no_update_carparks(mock_all_carparks_response, current_time)

        assert result == set()


def test_get_no_update_carparks_cache(mock_all_carparks_response):
    """
    Test the get_no_update_carparks function.

    This test verifies that the get_no_update_carparks function could cache the result.

    Parameters:
        mock_all_carparks_response: the mock all carpark ids response
    """
    # mock the make_api_request function to return the mock response
    with patch(
        "app.services.nsw_transport_api.get_all_carpark_ids",
        return_value=mock_all_carparks_response,
    ) as mock_api, patch(
        "app.services.nsw_transport_api.fetch_no_update_carparks", return_value=set()
    ) as mock_fetch:
        # first call: should call get_all_carpark_ids and fetch_no_update_carparks
        result1 = get_no_update_carparks()
        assert result1 == set()
        # second call: should hit the cache
        result2 = get_no_update_carparks()
        assert result2 == set()

        # verify the mock_api and mock_fetch is called only once
        assert mock_api.call_count == 1
        assert mock_fetch.call_count == 1


def test_get_carpark_locations_cache(
    mock_carpark_details, mock_all_carparks_response, mock_carpark_locations
):
    """
    Test the get_carpark_locations function.

    This test verifies that the get_carpark_locations function could cache the result.

    Parameters:
        mock_carpark_details: the mock carpark details
        mock_all_carparks_response: the mock all carpark ids response
        mock_carpark_locations: the mock carpark locations
    """
    # mock the get_carpark_details function to return the mock response
    # "222" and "333" are no-update
    with patch(
        "app.services.nsw_transport_api.get_carpark_details",
        return_value=mock_carpark_details,
    ) as mock_carpark_details, patch(
        "app.services.nsw_transport_api.get_all_carpark_ids",
        return_value=mock_all_carparks_response,
    ) as mock_all_carpark_ids, patch(
        "app.services.nsw_transport_api.get_no_update_carparks",
        return_value={"222", "333"},
    ) as mock_no_update_carparks:
        # first call: should call get_carpark_details,get_all_carpark_ids,get_no_update_carparks
        result1 = get_carpark_locations()
        print(result1)
        print(mock_carpark_locations)
        assert result1 == mock_carpark_locations
        # second call: should hit the cache
        result2 = get_carpark_locations()
        assert result2 == mock_carpark_locations

        # verify the mock_carpark_details,mock_all_carpark_ids,mock_no_update_carparks is called only once
        assert mock_carpark_details.call_count == 1
        assert mock_all_carpark_ids.call_count == 1
        assert mock_no_update_carparks.call_count == 1


def test_available_status():
    """
    Test the available_status function.
    """
    # Test different occupancy scenarios
    assert available_status(100, 0) == "Available"
    assert available_status(100, 80) == "Almost Full"
    assert available_status(100, 99) == "Almost Full"
    assert available_status(100, 100) == "Full"

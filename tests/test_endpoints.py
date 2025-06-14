# test endpoints
# test get_nearby_carparks
# test get_carpark_available_details

from unittest.mock import patch

import pytest

from app.api.v1.endpoints.carpark import verify_api_key
from app.main import app


@pytest.mark.asyncio
async def test_get_nearby_carparks_success(
    async_test_client, mock_carpark_locations, mock_headers, mock_api_key
):
    """
    Test the get_nearby_carparks endpoint.

    This test verifies that the get_nearby_carparks endpoint returns a list of carparks
    within a specified radius. It also checks that the response is valid and contains
    the expected data.

    Parameters:
        async_test_client: the async test client
        mock_carpark_locations: the mock carpark locations
        mock_headers: the mock headers
        mock_api_key: the mock api key
    """
    # override verify_api_key to always return valid
    app.dependency_overrides[verify_api_key] = lambda: mock_api_key

    # patch external data source
    with patch(
        "app.api.v1.endpoints.carpark.get_carpark_locations",
        return_value=mock_carpark_locations,
    ):
        response = await async_test_client.get(
            "/carparks/nearby?lat=-33.8145&lng=151.0096&radius_km=1",
            headers=mock_headers,
        )

    # assertions
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0, "No carparks found within radius"
    assert data[0]["facility_id"] == "111"
    assert data[0]["name"] == "carpark_1"
    assert data[0]["distance_km"] <= 1.0  # within 1km

    # cleanup
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_nearby_carparks_no_results(
    async_test_client, mock_headers, mock_api_key
):
    """
    Test the get_nearby_carparks endpoint.

    This test verifies that the get_nearby_carparks endpoint returns an empty list
    when no carparks are found within the specified radius. It also checks that the
    response is valid and contains the expected data.

    Parameters:
        async_test_client: the async test client
        mock_headers: the mock headers
        mock_api_key: the mock api key
    """
    app.dependency_overrides[verify_api_key] = lambda: mock_api_key
    with patch(
        "app.api.v1.endpoints.carpark.get_carpark_locations",
        return_value={"carparks": []},
    ):
        response = await async_test_client.get(
            "/carparks/nearby?lat=-33.8145&lng=151.0096&radius_km=1",
            headers=mock_headers,
        )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0, "Expected no carparks found within radius"
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_nearby_carparks_invalid_api_key(async_test_client, mock_headers):
    """
    Test the get_nearby_carparks endpoint.

    This test verifies that the get_nearby_carparks endpoint returns a 403 status code
    when an invalid API key is provided. It also checks that the response is valid and
    contains the expected data.

    Parameters:
        async_test_client: the async test client
        mock_headers: the mock headers
    """
    # provide a wrong api key
    response = await async_test_client.get(
        "/carparks/nearby?lat=-33.865&lng=151.209&radius_km=1",
        headers=mock_headers,
        # headers={"X-API-Key": {true value}} # add the correct api key here
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "The API Key is invalid."


@pytest.mark.asyncio
async def test_get_nearby_carparks_invalid_data_structure(
    async_test_client, mock_headers, mock_api_key
):
    """
    Test the get_nearby_carparks endpoint.

    This test verifies that the get_nearby_carparks endpoint with an invalid data structure.
    It should return a 200 status code and an empty list.

    Parameters:
        async_test_client: the async test client
        mock_headers: the mock headers
        mock_api_key: the mock api key
    """
    app.dependency_overrides[verify_api_key] = lambda: mock_api_key
    # patch the get_carpark_locations function to return an invalid data structure
    with patch(
        "app.api.v1.endpoints.carpark.get_carpark_locations",
        return_value={"carparks": {}},
    ):
        response = await async_test_client.get(
            "/carparks/nearby?lat=-33.865&lng=151.209&radius_km=1",
            headers=mock_headers,
        )

    assert response.status_code == 200
    assert response.json() == []
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_nearby_carparks_internal_server_error(
    async_test_client, mock_api_key, mock_headers
):
    """
    Test the get_nearby_carparks endpoint.

    This test verifies that the get_nearby_carparks endpoint returns a 500 status code
    when an exception is raised. It also checks that the response is valid and
    contains the expected data.

    Parameters:
        async_test_client: the async test client
        mock_api_key: the mock api key
        mock_headers: the mock headers
    """
    # override API key check to pass
    app.dependency_overrides[verify_api_key] = lambda: mock_api_key

    # simulate internal error: mock get_carpark_locations to raise an exception
    with patch(
        "app.api.v1.endpoints.carpark.get_carpark_locations",
        side_effect=Exception("Simulated failure"),
    ):
        response = await async_test_client.get(
            "/carparks/nearby?lat=-33.865&lng=151.209&radius_km=1",
            headers=mock_headers,
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
    app.dependency_overrides = {}


async def test_get_carpark_available_details_success(
    async_test_client, mock_api_key, mock_headers, mock_carpark_details
):
    """
    Test the get_carpark_available_details endpoint.

    This test verifies that the get_carpark_available_details endpoint returns the correct data
    when a valid facility_id is provided. It also checks that the response is valid and
    contains the expected data.

    Parameters:
        async_test_client: the async test client
        mock_api_key: the mock api key
        mock_headers: the mock headers
        mock_carpark_details: the mock carpark details
    """
    app.dependency_overrides[verify_api_key] = lambda: mock_api_key

    # patch the get_carpark_details function to return the mock carpark details
    # patch the get_no_update_carparks function to return an empty set
    # patch the available_status function to return "Available"
    with patch(
        "app.api.v1.endpoints.carpark.get_carpark_details",
        return_value=mock_carpark_details,
    ), patch("app.api.v1.endpoints.carpark.get_no_update_carparks", return_value=set()):

        response = await async_test_client.get("/carparks/111", headers=mock_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["facility_id"] == "111"
    assert data["name"] == "carpark_1"
    assert data["total_spots"] == 100
    assert data["available_spots"] == 40
    assert data["status"] == "Available"
    assert data["timestamp"] == "2025-06-12T10:00:00+10:00"
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_carpark_available_details_invalid_api_key(
    async_test_client, mock_headers
):
    """
    Test the get_carpark_available_details endpoint.

    This test verifies that the get_carpark_available_details endpoint returns a 403 status code
    when an invalid API key is provided. It also checks that the response is valid and
    contains the expected data.

    Parameters:
        async_test_client: the async test client
        mock_headers: the mock headers
    """
    # provide a wrong api key
    response = await async_test_client.get(
        "/carparks/111",
        headers=mock_headers,
        # headers={"X-API-Key": {true value}} # add the correct api key here
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "The API Key is invalid."


@pytest.mark.asyncio
async def test_get_carpark_available_details_no_update(
    async_test_client, mock_api_key, mock_headers
):
    """
    Test the get_carpark_available_details endpoint.

    This test verifies that the get_carpark_available_details endpoint returns a 200 status code
    when a valid facility_id is provided. It also checks that the response is valid and
    contains the expected data.

    Parameters:
        async_test_client: the async test client
        mock_api_key: the mock api key
        mock_headers: the mock headers
    """
    app.dependency_overrides[verify_api_key] = lambda: mock_api_key

    with patch(
        "app.api.v1.endpoints.carpark.get_no_update_carparks", return_value={"222"}
    ):
        response = await async_test_client.get("/carparks/222", headers=mock_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "No Data Available"
    assert data["available_spots"] == 0
    assert data["timestamp"] is None

    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_carpark_available_details_not_found(
    async_test_client, mock_api_key, mock_headers
):
    """
    Test the get_carpark_available_details endpoint.

    This test verifies that the get_carpark_available_details endpoint returns a 404 status code
    when a non-existent facility_id is provided. It also checks that the response is valid and
    contains the expected data.

    Parameters:
        async_test_client: the async test client
        mock_api_key: the mock api key
        mock_headers: the mock headers
    """
    app.dependency_overrides[verify_api_key] = lambda: mock_api_key

    with patch(
        "app.api.v1.endpoints.carpark.get_carpark_details", return_value=None
    ), patch("app.api.v1.endpoints.carpark.get_no_update_carparks", return_value=set()):
        response = await async_test_client.get("/carparks/000", headers=mock_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Carpark with ID 000 not found"

    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_carpark_available_details_invalid_data(
    async_test_client, mock_api_key, mock_headers, mock_carpark_details
):
    """
    Test the get_carpark_available_details endpoint.

    This test verifies that the get_carpark_available_details endpoint returns a 500 status code
    when the detail data is invalid (e.g., bad 'spots' or 'occupancy'). It also checks that the
    response is valid and contains the expected data.

    Parameters:
        async_test_client: the async test client
        mock_api_key: the mock api key
        mock_headers: the mock headers
        mock_carpark_details: the mock carpark details
    """
    app.dependency_overrides[verify_api_key] = lambda: mock_api_key

    # patch the get_carpark_details function to return an invalid data structure
    mock_carpark_details["spots"] = "invalid"

    with patch(
        "app.api.v1.endpoints.carpark.get_no_update_carparks", return_value=set()
    ), patch(
        "app.api.v1.endpoints.carpark.get_carpark_details",
        return_value=mock_carpark_details,
    ):
        response = await async_test_client.get("/carparks/001", headers=mock_headers)

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"

    app.dependency_overrides = {}

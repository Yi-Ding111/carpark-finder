# provide mock data for testing

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport

@pytest.fixture
def test_client():
    """
    Set up a test client for the FastAPI
    """
    return TestClient(app)


@pytest.fixture
def mock_url():
    """
    Return a mock URL for testing
    """
    return "https://example.com"


@pytest.fixture
async def async_test_client(mock_url):
    """
    Set up an async test client for the FastAPI
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=mock_url) as ac:
        yield ac


@pytest.fixture
def mock_api_key():
    """
    Return a mock API key for testing
    """
    return "mock_api_key"


@pytest.fixture
def mock_headers(mock_api_key):
    """
    Return a mock headers for testing
    """
    return {"X-API-Key": mock_api_key}


@pytest.fixture
def invalid_headers():
    """
    Return a mock invalid headers for testing
    """
    return {"X-API-Key": "invalid_key"}


@pytest.fixture
def missing_headers():
    """
    Return a mock missing headers for testing
    """
    return {}


@pytest.fixture
def mock_success_response():
    """
    Return a mock success response for testing
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "ok"}
    mock_response.raise_for_status.return_value = None
    return mock_response


@pytest.fixture
def mock_sydney_local_time():
    """
    Use a mock local time for testing
    """
    return "2025-06-12T11:08:35"


@pytest.fixture
def mock_all_carparks_response():
    """
    Return a mock all carpark response for testing
    """
    return {
        "111": "carpark_1",
        "222": "carpark_2",
        "333": "carpark_3",
    }


@pytest.fixture
def mock_carpark_locations():
    """
    Return mock carpark locations data.
    """
    return {
        "carparks": [
            {
                "facility_id": "111",
                "name": "carpark_1",
                "location": {"latitude": -33.814583, "longitude": 151.009659},
            }
        ]
    }


@pytest.fixture
def mock_carpark_details():
    """
    Return mock carpark available details.
    """
    return {
        "tsn": "1234567",
        "facility_id": "111",
        "spots": "100",
        "facility_name": "carpark_1",
        "location": {"latitude": "-33.814583", "longitude": "151.009659"},
        "occupancy": {"total": "60"},
        "MessageDate": "2025-06-12T10:00:00",
    }

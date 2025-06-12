# provide mock data for testing
# mock data for carpark locations
# mock data for carpark details
# mock data for carpark status
# mock data for carpark occupancy
# mock data for carpark message date
# mock data for carpark message time
# mock data for carpark message timezone
# mock data for carpark message timestamp

import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def test_client():
    """
    Set up a test client for the FastAPI
    """
    return TestClient(app)


@pytest.fixture
def mock_api_key():
    """
    Use a mock API key for testing
    """
    return "test_api_key"


@pytest.fixture
def mock_sydney_local_time():
    """
    Use a mock local time for testing
    """
    return "2025-06-12T11:08:35"


@pytest.fixture
def mock_carpark_locations():
    """
    Return mock carpark locations data.
    """
    return {
        "carparks": [
            {
                "facility_id": "test_id_1",
                "name": "test_name_1",
                "location": {
                    "latitude": "-33.814583",
                    "longitude": "151.009659"
                }
            },
            {
                "facility_id": "test_id_2",
                "name": "test_name_2",
                "location": {
                    "latitude": "-33.856785",
                    "longitude": "151.215302"
                }
            }
        ]
    }


@pytest.fixture
def mock_carpark_details():
    """
    Return mock carpark available details.
    """
    return {
        "facility_id": "CP001",
        "facility_name": "Test Carpark 1",
        "spots": "100",
        "occupancy": {
            "total": "60"
        },
        "MessageDate": "2024-03-20T10:00:00Z"
    } 
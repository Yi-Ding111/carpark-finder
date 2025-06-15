import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
NSW_API_KEY = os.getenv("NSW_CARPARK_API_TOKEN")
PUBLIC_API_TOKEN = os.getenv("PUBLIC_API_TOKEN")

# Cache settings
CACHE_TTL = 60 * 60 * 1  # 1 hour
CACHE_MAXSIZE = 128

# API rate limiting
MAX_REQUESTS_PER_SECOND = 5

# Check if required API keys are set
if not NSW_API_KEY:
    raise ValueError("NSW_CARPARK_API_TOKEN not found in environment variables")
if not PUBLIC_API_TOKEN:
    raise ValueError("PUBLIC_API_TOKEN not found in environment variables")


# NSW Transport URL
NSW_TRANSPORT_BASE_API_URL = "https://api.transport.nsw.gov.au/v1/carpark"


# Get NSW Transport API headers
def get_nsw_headers():
    """
    Get NSW Transport API headers

    Returns:
        dict: NSW Transport API headers
    """
    return {"Authorization": f"apikey {NSW_API_KEY}", "Accept": "application/json"}


# Get NSW Transport API URL for a specific facility
def get_facility_url(facility_id: str = None) -> str:
    """
    Construct URL for NSW Carpark API.

    Args:
        facility_id (str, optional): If provided, returns URL for a specific facility.

    Returns:
        str: Full URL to call.
    """
    if facility_id:
        return f"{NSW_TRANSPORT_BASE_API_URL}?facility={facility_id}"
    return NSW_TRANSPORT_BASE_API_URL

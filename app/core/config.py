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

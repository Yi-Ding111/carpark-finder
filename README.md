# carpark-finder

A REST API service that helps users find and get real-time information about nearby car parks in NSW. The service provides location-based search, availability data, and detailed carpark information.


## project structure

```
carpark-finder/
├── app/                    # Main application package
│   ├── api/               # API endpoints and route handlers
│   ├── core/              # Core functionality like security and config
│   ├── models/            # Pydantic models and data schemas
│   ├── services/          # External API integrations and business logic
│   └── utils/             # Helper functions for distance, time etc.
├── tests/                 # Test files and test utilities
├── openapi/              # OpenAPI/Swagger specification files
├── .github/              # GitHub Actions workflows CI/CD
├── .env.example          # Example environment variables
├── requirements.txt      # Production dependencies
├── Dockerfile           # Docker container configuration
└── run.py               # Application entry point
```

## Key Features

- Find nearby car parks using location coordinates and radius
- Real-time availability spots for each carpark
- Distance calculation using Haversine formula
- API key authentication
- Rate limiting and caching for optimal performance

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/Yi-Ding111/carpark-finder.git
cd carpark-finder
```
2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```
3. Environment Configuration

The `.env` file requires two API tokens:
```
NSW_CARPARK_API_TOKEN= {get from https://opendata.transport.nsw.gov.au/developers/userguide}
PUBLIC_API_TOKEN= {choose any token, e.g. AcQhJ8MD0lGDPvNpTCgFYhdwewn90neftYZkm}
** You must make sure you pass the key you generate into the header when you want to get request.**
```

Choose one of the following methods to set up the project:

### Method 1: Using Conda (Recommended for Development)

1. Install [Conda](https://docs.conda.io/en/latest/miniconda.html) if you haven't already
2. Create and activate the environment:
```bash
conda env create -f environment.yaml
conda activate carpark
```
3. Run the application:
```bash
python run.py
```

### Method 2: Using Docker

1. Install [Docker](https://docs.docker.com/get-docker/) if you haven't already
2. Build and run the container:
```bash
# Build the image
docker build -t carpark-finder .

# Run the container with environment variables
docker run -p 8000:8000 --env-file .env carpark-finder
```

### Method 3: Using pip

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate 
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python run.py
```

### Method 4: AWS-based deployment
- I deployed this servcide through AWS services
- Because I hope the code could run in different local env, I direct use AWS ECR, ECS, API gateway and deploy it on cloud. 

---
---

Once the application is running, you can access:
- Swagger UI: http://localhost:8000/docs (default redirect)


Besides requesting through UI, you could do request through terminal.
### Find Nearby Car Parks

```bash
curl -X GET "http://localhost:8000/carparks/nearby?lat=-33.748043&lng=150.69444&radius_km=10" \
     -H "x-api-key: YOUR_API_KEY"
```
Response:
```json
[
  {
    "facility_id": "111",
    "name": "Carpark 1",
    "distance_km": 1.5
  }
]
```

### Find carpark details (availbility)

```
curl -X GET "http://localhost:8000/carparks/8" \
     -H "x-api-key: YOUR_API_KEY"
```
Response:
```json
{
  "facility_id": "111",
  "name": "Carpark 1",
  "total_spots": 100,
  "available_spots": 25,
  "status": "Available",
  "timestamp": "2025-06-14T16:35:23+10:00"
}
```

### Openpai Spec
- **More details about this API could be found through [openapi.json](./openapi/openapi.yaml)**


### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- openapi.json: http://localhost:8000/openapi.json


### Test Coverage Report
- The test coverage report is deployed in Github Page
- could get access through https://yi-ding111.github.io/carpark-finder/


## Important Notes

### Data Assumptions
- Carparks must update at least once every 24 hours to be considered active
- Historical carparks (IDs 1-5) do not have useful data (only about historical data)
- Availability is calculated as: `spots - total`.
- For declaration: Only use `total` value under `occupancy`. Don't use that under `Zone`.
- Status indicators:
  - "Full": < 1 spot available
  - "Almost Full": <= 10% of total capacity available
  - "Available": >10% of total capacity available

### Known Limitations
- Zone occupancy data may be inconsistent for carparks:
  - Ashfield (486)
  - Kogarah (487)
  - Seven Hills (488)
  - Manly Vale (489)
  - Brookvale (490)
- Total occupancy calculations are not affected by zone information issues

### API Limits (Bronze Plan)
- Daily quota: 60,000 requests
- Rate limit: 5 requests per second
- HTTP 429 errors are handled automatically within this API service
- This API service also ask 5 request per second limit.


### Caching Strategy
- Initial requests may take a few seconds to fetch fresh data from NSW Transport API
- Responses are cached for 1 hour to improve performance of subsequent requests
- Cache is automatically invalidated after 1 hour to ensure data freshness
- The cache is not about the carpark details, only for the active carpark ids.

# carpark-finder


## Features

- Find nearby car parks based on location and radius
- Get detailed information about specific car parks
- Real-time availability data
- Rate limiting and caching
- Secure API access

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/carpark-finder.git
cd carpark-finder
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

4. Copy `.env.example` to `.env` and fill in your configuration:
```bash
cp .env.example .env
```

5. Run the application:
```bash
python run.py
```

## API Documentation

Once the application is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Implementation Details

### Car Park Data
- The service excludes facility IDs 1-5 as they contain historical data and are not suitable for real-time availability information
- Each car park must update at least once every 24 hours to be considered active
- TTL caching is implemented for certain endpoints (e.g., `get_all_carpark_ids()`)

### Location-Based Search
- Uses Haversine formula to calculate distances between user location and car parks
- Requires latitude, longitude, and radius (in km) as input parameters
- Example request:
  ```sh
  curl -X GET "http://localhost:8000/carparks/nearby?lat=-33.748043&lng=150.69444&radius_km=10" \
       -H "x-api-key: {API_KEY}"
  ```

### Availability Calculation
1. Available spots = total capacity - current occupancy
2. Uses the "total" field from facility occupancy object for accurate estimates
3. Status indicators:
   - "Full": When available spots < 1
   - "Almost Full": When available spots < 10% of total capacity (configurable)
   - Uses "~" symbol to indicate approximate availability

### Known Limitations
- Zone occupancy information may have inconsistencies for facilities:
  - 486 (Ashfield)
  - 487 (Kogarah)
  - 488 (Seven Hills)
  - 489 (Manly Vale)
  - 490 (Brookvale)
- Total occupancy calculations are not affected by zone information issues

### API Rate Limits
Default "Bronze Plan" limits:
- Daily quota: 60,000 requests
- Rate limit: 5 requests per second
- Implements handling for HTTP 429 (Too Many Requests) errors

### Authentication
- API access requires an API key
- Currently uses static API keys for simplicity
- Can be extended to support dynamic API key generation if needed

## Development

### Running Tests
```bash
pytest
```

The project includes unit tests to verify:
- Proper exclusion of historical facility IDs (1-5)
- Facility update frequency validation
- API rate limiting functionality

### Code Quality
```bash
# Run linting
flake8

# Run type checking
mypy .

# Run formatting
black .
```



## Testing
The project includes unit tests to verify:
- Proper exclusion of historical facility IDs (1-5)
- Facility update frequency validation
- API rate limiting functionality

if i want to get the list of carparks based off the location and distance. I need to provide my location and do calculation with the park&ride locations. 

after querying, I found that the carparks with facility ids: 1,2,3,4,5 is about historical data, they cannot meet what we need right here. So I would drop them during the calculation. (more details, when qeurying facility_id is 1 or 2, we cannot get the resource.)


so I should add the unit test for this. check the carparks id, ensure that each facility's updates are working efficiently.






The default account plan is the "Bronze Plan", which has the following limits:

Quota: 60,000 per day

Rate Limit: 5 per second

based off these limitations, I need to add the corresponding actions in the code to avoid the problem.

if facing http error 429: too many requests. 









for the radium km limitation, I would calculate all distances between the current location and the carpark's location by Haversine formula.



availability:



To calculate the number of available parking lots, it is recommended to use the following formula.
Availability = spots – total
2. Displays the number of parking lots left in the car park facility. Use the “total” in facility occupancy object
for an accurate estimates of occupancy information of the car park.
3. Calculate and display “Full” when the available parking lots drop below 1.
4. Display “Almost Full” when the available parking lots drop to less than 10%. This figure should be
configurable and adjusted according to customers’ feedback.
5. To manage customers’ expectations, indicate that the car park data may differ from actual parking. It is
recommended to put that the approximate sign (~) to inform the customers that this is an estimated car
park availability information.



about the the zone occupancy information, it may has some problems for: 486 (Ashfield), 487 (Kogarah), 488 (Seven Hills), 489 (Manly Vale), 490 (Brookvale). But I assume the total number under Occupancy does not influeced by the information in Zone. 









for the API i created:

I want to deploy it as an open api and everyone could use it, but with API token

for the easy development, I only use the static API key right here, I could update as dynamic API keys if necessary.






about the update frequence:

because some carparks follow on counter change rule. I do not know about the exact update frequence. So I define that each carpark have the update at least once each day. If one carpark does not update over 24 hours, I have reason to say that the carpark is no update and do not cover them in consideration.


I set up some ttl cache for some requests: get_all_carpark_ids(), 


how to get the request

```sh
curl -X GET "http://localhost:8000/carparks/nearby?lat=-33.748043&lng=150.69444&radius_km=10" \
     -H "x-api-key: {API_KEY}"
```
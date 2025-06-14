import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.v1.endpoints import carpark
from app.core.logging_config import setup_logging

# Initialize logging
logger = setup_logging()

# FastAPI entry point
app = FastAPI(
    title="Carpark Finder API",
    description="It is an API service to find nearby carparks (Park&Ride) in NSW",
    version="1.0.0",
)


# Load custom OpenAPI schema
def custom_openapi():
    """
    Custom OpenAPI schema
    """
    if app.openapi_schema:
        return app.openapi_schema
    with open("openapi/openapi.yaml", "r") as f:
        openapi_dict = yaml.safe_load(f)
        app.openapi_schema = openapi_dict
        return app.openapi_schema


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["X-API-Key"],
)

# Include routers
app.include_router(carpark.router, prefix="/carparks", tags=["carparks"])

# Custom OpenAPI schema
app.openapi = custom_openapi


@app.get("/")
def read_root():
    """Redirect to the Swagger UI page as default page"""
    logger.info("Redirecting to Swagger UI")
    return RedirectResponse(url="/docs")


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

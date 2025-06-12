from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.api.v1.endpoints import carpark
from app.core.logging_config import setup_logging
import logging

# Initialize logging
logger = setup_logging()

# FastAPI entry point
app = FastAPI(
    title="Carpark Finder API",
    description="It is an API service to find nearby carparks (Park&Ride) in NSW",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This project is not for production, so we allow all origins
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["X-API-Key"],  # This is the header name for the API key
)

# Include routers
app.include_router(carpark.router, prefix="/carparks", tags=["carparks"])


@app.get("/")
def read_root():
    """Redirect to the Swagger UI page as default page"""
    logger.info("Redirecting to Swagger UI")
    return RedirectResponse(url="/docs")


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

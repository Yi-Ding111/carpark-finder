from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

from app.core.config import PUBLIC_API_TOKEN

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


async def verify_api_key(
    api_key_header: str = Security(api_key_header)
) -> str:
    """
    Validates the API key provided in the request header against the stored PUBLIC_API_TOKEN.
    This function is used as a dependency to protect API endpoints.

    Parameters:
        api_key_header (str): The API key extracted from the X-API-Key header.
                             Automatically handled by FastAPI's Security dependency.

    Returns:
        str: The validated API key if successful.

    Raises:
        HTTPException: 403 Forbidden error if the API key is invalid.
    """
    if api_key_header != PUBLIC_API_TOKEN:
        raise HTTPException(status_code=403, detail="The API Key is invalid.")
    return api_key_header

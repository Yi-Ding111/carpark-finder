from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Carpark(BaseModel):
    facility_id: str
    name: str
    distance_km: float


class CarparkDetail(BaseModel):
    facility_id: str
    name: str
    total_spots: int
    available_spots: int
    status: str
    timestamp: Optional[datetime]

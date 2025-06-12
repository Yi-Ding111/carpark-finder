from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Carpark(BaseModel):
    facility_id: int
    name: str
    distance_km: float


class CarparkDetail(BaseModel):
    facility_id: str
    name: str
    total_spots: int
    available_spots: int
    status: str
    timestamp: Optional[datetime]

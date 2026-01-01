from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AgentDetailResponse(BaseModel):
    id: int
    username: str
    email: str
    phone_number: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    status: str
    country: Optional[str]
    state: Optional[str]
    city_of_residence: Optional[str]
    created_date: datetime

    agent_code: str
    commission_percentage: float
    assigned_region: Optional[str]
    kyc_status: str
    is_active: bool

    class Config:
        json_schema_extra = {
            "example": {
                "id": 5,
                "username": "agent_rahul",
                "email": "rahul.sharma@gmail.com",
                "phone_number": "9876543210",
                "first_name": "Rahul",
                "last_name": "Sharma",
                "role": "agent",
                "status": "active",
                "nationality": "Indian",
                "state": "Telangana",
                "city_of_residence": "Hyderabad",
                "created_date": "2025-01-12T10:30:00",

                "agent_code": "AGT-5",
                "commission_percentage": 12.5,
                "assigned_region": "Hyderabad",
                "kyc_status": "verified",
                "is_active": True
            }
        }

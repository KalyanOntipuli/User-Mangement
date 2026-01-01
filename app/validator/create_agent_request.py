from typing import Literal
from pydantic import BaseModel, EmailStr, Field


class CreateAgentRequest(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    email: EmailStr
    first_name: str = Field(min_length=2, max_length=25)
    last_name: str = Field(min_length=2, max_length=25)
    gender: Literal["male", "female", "other"]
    phone_number: str = Field(min_length=10, max_length=15)
    password: str = Field(min_length=8, max_length=20)
    commission_percentage: float = Field(..., ge=0, le=100)
    assigned_region: str | None = None

    class Config:
        schema_extra = {
            "example": {
                "username": "agent_rahul",
                "email": "rahul.sharma@gmail.com",
                "first_name": "kalyan",
                "last_name": "ontipuli",
                "gender": "male",
                "phone_number": "9876543210",
                "password": "Secret@123",
                "commission_percentage": 12.5,
                "assigned_region": "Hyderabad",
            }
        }

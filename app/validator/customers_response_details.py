from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class CustomerResponseDetails(BaseModel):
    id: int
    username: str
    email: str
    phone_number: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    status: str
    nationality: Optional[str]
    state: Optional[str]
    city_of_residence: Optional[str]
    created_date: datetime

    date_of_birth: Optional[date]
    passport_no: Optional[str]
    passport_expiry_date: Optional[date]
    passport_issuing_country: Optional[str]
    pancard_number: Optional[str]
    emergency_contact: Optional[str]
    preferred_language: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "id": 21,
                "username": "john_doe",
                "email": "john.doe@gmail.com",
                "phone_number": "9876543210",
                "first_name": "John",
                "last_name": "Doe",
                "role": "customer",
                "status": "active",
                "nationality": "Indian",
                "state": "Telangana",
                "city_of_residence": "Hyderabad",
                "created_date": "2025-01-15T09:45:00",

                "date_of_birth": "1995-08-20",
                "passport_no": "A1234567",
                "passport_expiry_date": "2035-08-19",
                "passport_issuing_country": "India",
                "pancard_number": "ABCDE1234F",
                "emergency_contact": "9988776655",
                "preferred_language": "English"
            }
        }

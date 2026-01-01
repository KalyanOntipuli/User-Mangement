from pydantic import BaseModel, EmailStr, Field, validator
from datetime import date
from typing import Literal


class UserModel(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    phone_number: str = Field(min_length=10, max_length=15)
    password: str = Field(min_length=8, max_length=25)

    first_name: str = Field(min_length=2, max_length=25)
    last_name: str = Field(min_length=2, max_length=25)

    gender: Literal["male", "female", "other"]
    country: str = Field(default="India")

    date_of_birth: date = Field(..., description="Date of birth in YYYY-MM-DD format")

    # ✅ Pydantic v1 validator
    @validator("date_of_birth")
    def validate_date_of_birth(cls, dob: date):
        today = date.today()

        if dob >= today:
            raise ValueError("Date of birth cannot be in the future")

        age = today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )

        if age < 18:
            raise ValueError("User must be at least 18 years old")

        if age > 120:
            raise ValueError("Invalid date of birth")

        return dob

    class Config:
        schema_extra = {
            "example": {
                "username": "kalyan",
                "email": "kalyanontipuli123@gmail.com",
                "phone_number": "9398662859",
                "password": "Secret@123",
                "first_name": "Kalyan",
                "last_name": "Ontipuli",
                "gender": "male",
                "country": "India",
                "date_of_birth": "1999-05-20",
            }
        }

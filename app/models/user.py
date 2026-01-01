import re
from app.models import Base
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Boolean,
    func,
)
from sqlalchemy.orm import validates, relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    gender = Column(String)
    date_of_birth = Column(Date, nullable=True)

    phone_number = Column(String(15), nullable=False)
    country = Column(String(100))
    state = Column(String(100))
    city_of_residence = Column(String(100))

    role = Column(String, default="customer")
    status = Column(String, default="active")

    otp = Column(String, nullable=True)
    otp_expires = Column(DateTime, nullable=True)

    created_by = Column(String)
    modified_by = Column(String)
    created_date = Column(DateTime(timezone=False), server_default=func.now())
    modified_date = Column(DateTime(timezone=False), onupdate=func.now())

    @validates("email")
    def validate_email(self, key, value):
        email_regex = r"^[^@]+@[^@]+\.[^@]+$"
        if not re.match(email_regex, value):
            raise ValueError("Invalid email format")
        return value.lower()

    @validates("phone_number")
    def validate_phone(self, key, value):
        if not value.isdigit() or len(value) not in (10, 11, 12):
            raise ValueError("Invalid phone number")
        return value

    @validates("status")
    def validate_status(self, key, value):
        allowed = {"active", "inactive", "suspended"}
        if value not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return value

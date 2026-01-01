import re
from app.models import Base
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Boolean,
    func,
)
from sqlalchemy.orm import validates, relationship


class CustomerProfile(Base):
    __tablename__ = "customer_profiles"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    passport_no = Column(String(20), nullable=True)
    passport_expiry_date = Column(Date, nullable=True)
    passport_issuing_country = Column(String(100), nullable=True)

    pancard_number = Column(String(10), nullable=True)
    emergency_contact = Column(String(15), nullable=True)
    preferred_language = Column(String(50), nullable=True)

    qualifying_trips_count = Column(Integer, default=0)
    total_qualifying_amount = Column(Numeric(12, 2), default=0.00)

    completed_trips_count = Column(Integer, default=0)
    free_trip_earned_count = Column(Integer, default=0)
    free_trip_used_count = Column(Integer, default=0)

    last_trip_date = Column(DateTime, nullable=True)


    @validates("passport_no")
    def validate_passport(self, key, value):
        if value and not re.match(r"^[A-Z0-9]{6,9}$", value):
            raise ValueError("Invalid passport number")
        return value

    @validates("passport_expiry_date")
    def validate_passport_expiry(self, key, value):
        if value and self.date_of_birth and value <= self.date_of_birth:
            raise ValueError("Passport expiry must be after date of birth")
        return value

    @validates("pancard_number")
    def validate_pancard(self, key, value):
        if value and not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", value):
            raise ValueError("Invalid PAN card number")
        return value

    @validates("emergency_contact")
    def validate_emergency_contact(self, key, value):
        if value and (not value.isdigit() or len(value) not in (10, 11, 12)):
            raise ValueError("Invalid emergency contact number")
        return value

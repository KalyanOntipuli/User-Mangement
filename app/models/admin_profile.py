from app.models import Base
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship, validates

class AdminProfile(Base):
    __tablename__ = "admin_profiles"

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    department = Column(String(100), nullable=False)
    access_level = Column(String(20), nullable=False) # SUPER, FINANCE, OPERATIONS, SUPPORT, AUDIT

    @validates("access_level")
    def validate_access_level(self, key, value):
        allowed = {"SUPER", "FINANCE", "OPERATIONS", "SUPPORT", "AUDIT"}
        if value not in allowed:
            raise ValueError(f"access_level must be one of {allowed}")
        return value

    @validates("department")
    def validate_department(self, key, value):
        if not value or len(value.strip()) < 2:
            raise ValueError("department must be a valid string")
        return value.strip()

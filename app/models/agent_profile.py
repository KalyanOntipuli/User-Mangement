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
    Numeric,
    func,
)
from sqlalchemy.orm import validates, relationship


class AgentProfile(Base):
    __tablename__ = "agent_profiles"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    agent_code = Column(String(50), unique=True, nullable=False)
    commission_percentage = Column(Numeric(5, 2), nullable=False)
    assigned_region = Column(String(100), nullable=True)
    kyc_status = Column(String(20), default="pending")
    kyc_document_ref = Column(String(255), nullable=True)
    bank_account_number = Column(String(30), nullable=True)
    bank_ifsc_code = Column(String(15), nullable=True)
    bank_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    onboarded_date = Column(Date, server_default=func.current_date())
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now())
    
    @validates("commission_percentage")
    def validate_commission(self, key, value):
        if value < 0 or value > 100:
            raise ValueError("Commission percentage must be between 0 and 100")
        return value

    @validates("kyc_status")
    def validate_kyc_status(self, key, value):
        allowed = {"pending", "verified", "rejected"}
        if value not in allowed:
            raise ValueError(f"KYC status must be one of {allowed}")
        return value

    @validates("bank_ifsc_code")
    def validate_ifsc(self, key, value):
        if value and not re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", value):
            raise ValueError("Invalid IFSC code")
        return value

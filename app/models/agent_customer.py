from app.models import Base
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy.orm import relationship


class AgentCustomer(Base):
    __tablename__ = "agent_customers"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    customer_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    is_active = Column(Boolean, default=True)
    assigned_date = Column(Date, server_default=func.current_date())
    created_at = Column(DateTime(timezone=False), server_default=func.now())
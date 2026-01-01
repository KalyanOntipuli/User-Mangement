from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import relationship
from app.models import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    agent_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    booking_date = Column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=False,
    )

    total_amount = Column(
        Numeric(12, 2),
        nullable=False,
    )

    status = Column(
        String(30),
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=False,
    )
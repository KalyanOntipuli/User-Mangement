from sqlalchemy import (
    JSON,
    Column,
    Float,
    Integer,
    String,
    ForeignKey,
    DateTime,
    func,
    Boolean,
)
from app.models import Base


class TransactionHistory(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    payment_method_type = Column(String)
    txn_no = Column(Integer)
    currency = Column(String)
    price = Column(Float)

    customer_name = Column(String)
    customer_email = Column(String)
    customer_phone_number = Column(String)

    payment_id = Column(String)
    payment_method = Column(JSON)
    payment_status = Column(String)
    transaction_time = Column(String)

    is_active = Column(Boolean, default=True)

    created_by = Column(String)
    modified_by = Column(String)

    created_date = Column(DateTime(timezone=False), server_default=func.now())
    modified_date = Column(DateTime(timezone=False), onupdate=func.now())

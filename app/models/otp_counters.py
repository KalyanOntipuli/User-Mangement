from app.models import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from datetime import timedelta, datetime


class OtpCounters(Base):
    __tablename__ = "otpcounters"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    signup_otp_count = Column(Integer, default=0)
    signup_latest_otp_requested_date = Column(DateTime)
    account_reactivation_otp_count = Column(Integer, default=0)
    account_reactivation_latest_otp_requested_date = Column(DateTime)
    forgot_password_otp_count = Column(Integer, default=0)
    forgot_password_latest_otp_requested_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_by = Column(String)
    modified_by = Column(String)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    modified_date = Column(DateTime(timezone=True), onupdate=func.now())

    def is_signup_count_exceeded(self):
        if (
            self.signup_latest_otp_requested_date
            and self.signup_latest_otp_requested_date + timedelta(hours=3)
            < datetime.now()
        ):
            return self.id
        return None

    def is_forgot_password_count_exceeded(self):

        if (
            self.forgot_password_latest_otp_requested_date
            and self.forgot_password_latest_otp_requested_date + timedelta(hours=3)
            < datetime.now()
        ):
            return self.id
        return None

    def is_account_activation_count_exceeded(self):

        if (
            self.account_reactivation_latest_otp_requested_date
            and self.account_reactivation_latest_otp_requested_date + timedelta(hours=3)
            < datetime.now()
        ):
            return self.id
        return None

import io
import os
import logging

import requests
from datetime import datetime, timedelta
from typing import Annotated, Any, Optional
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
    Query,
)
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import EmailStr
from sqlalchemy.orm import Session
from app.infra.functions import get_current_time
from app.infra.notifications import send_notification
from app.models.otp_counters import OtpCounters
from app.models import SessionLocal
from app.infra.email_templates import (
    get_otp_template,
)
from app.models.user import User
from app.validator.user_validator import UserModel
from app.models.user_activity import UserActivity
from app.routers.auth import (
    decrypt_api_key,
    generate_unique_otp,
    get_current_user,
    encrypt_api_key,
    get_password_hash,
    encode_otp,
    encrypted_api_key,
)
from app.utilities.constants import (
    AUTHORIZATION_HEADER_KEY,
    DEV_API_URL,
)

router = APIRouter(prefix="/user", tags=["user"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/check_username_existence")
async def check_username_existence(
    username: str,
    db: db_dependency,
    encrypted_api_key: encrypted_api_key,
):
    try:
        if decrypt_api_key(encrypted_api_key) != AUTHORIZATION_HEADER_KEY:
            return JSONResponse(
                {"detail": "Invalid encrypted_api_key"},
                status_code=status.HTTP_403_FORBIDDEN,
            )
        db_user = db.query(User).filter(User.username == username).first()
        if db_user:
            return True
        return False

    except Exception as e:
        return JSONResponse(
            {"detail": f"An unexpected error occurred: {str(e)}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    finally:
        if db:
            db.close()


@router.get("/check_email_existence")
async def check_email_existence(
    db: db_dependency,
    encrypted_api_key: encrypted_api_key,
    email: EmailStr = Query(...),
):
    try:
        print(encrypted_api_key)

        if decrypt_api_key(encrypted_api_key) != AUTHORIZATION_HEADER_KEY:
            return JSONResponse(
                {"detail": "Invalid encrypted_api_key"},
                status_code=status.HTTP_403_FORBIDDEN,
            )

        db_user = db.query(User).filter(User.email == email).first()

        if db_user:
            return True

        return False

    except Exception as e:
        return JSONResponse(
            {"detail": f"An unexpected error occurred: {str(e)}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    finally:
        if db:
            db.close()


@router.get("/check_phone_number_existence")
async def check_phone_number_existence(
    db: db_dependency, encrypted_api_key: encrypted_api_key, phone_number: str
):
    try:
        if decrypt_api_key(encrypted_api_key) != AUTHORIZATION_HEADER_KEY:
            return JSONResponse(
                {"detail": "Invalid encrypted_api_key"},
                status_code=status.HTTP_403_FORBIDDEN,
            )

        db_user = db.query(User).filter(User.phone_number == phone_number).first()

        if db_user:
            return True

        return False

    except Exception as e:
        return JSONResponse(
            {"detail": f"An unexpected error occurred: {str(e)}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    finally:
        if db:
            db.close()


@router.post("/send_signup_otp")
async def send_signup_otp(
    db: db_dependency,
    encrypted_api_key: encrypted_api_key,
    email: Optional[EmailStr] = Query(None),
    phone_number: Optional[str] = Query(None),
):
    try:
        if decrypt_api_key(encrypted_api_key) != AUTHORIZATION_HEADER_KEY:
            return JSONResponse(
                {"detail": "Invalid encrypted_api_key"},
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if not email and not phone_number:
            return JSONResponse(
                {"detail": "Either email or phone number must be provided"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if email and phone_number:
            return JSONResponse(
                {
                    "detail": "Only either email or phone number can be assigned, not both"
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        otp = generate_unique_otp()

        if email:
            otp_info = "Thanks for registering with Markwave"
            otp_purpose = "Sign Up"
            html_content = get_otp_template("User", otp, otp_purpose, otp_info)
            subject = "OTP for Sign Up"
            await send_notification(email, subject, html_content)

        elif phone_number:

            signup_user = (
                db.query(OtpCounters)
                .filter(OtpCounters.phone_number == phone_number)
                .first()
            )

            if signup_user:
                if signup_user.signup_otp_count >= 3:
                    return JSONResponse(
                        {
                            "detail": "You have reached the maximum OTP limit. Please try again later or use email."
                        },
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    signup_user.signup_otp_count += 1
                    signup_user.signup_latest_otp_requested_date = datetime.now()
                    db.commit()
            else:
                signup_user_model = OtpCounters(
                    phone_number=phone_number,
                    signup_latest_otp_requested_date=datetime.now(),
                    created_by=phone_number,
                    signup_otp_count=1,
                )
                db.add(signup_user_model)
                db.commit()

        response_data = {
            "user_email": email,
            "user_phone_number": phone_number,
            "otp": encrypt_api_key(str(encode_otp(1234))),
            "otp_requested_time": get_current_time(),
            "otp_expiry_time": get_current_time() + timedelta(minutes=5),
        }

        if email:
            response_data["user_email"] = email
        elif phone_number:
            response_data["user_phone_number"] = phone_number

        return {
            "message": f"OTP sent to your {'email' if email else 'phone_number'}. Use it to for your sign up.",
            "response": response_data,
            "status_code": status.HTTP_200_OK,
        }

    except Exception as error:
        return JSONResponse(
            {"detail": f"An unexpected error occurred: {str(error)}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/create_normal_user")
async def create_user(
    encrypted_api_key: encrypted_api_key,
    user_model: UserModel,
    db: db_dependency,
):
    try:
        if decrypt_api_key(encrypted_api_key) != AUTHORIZATION_HEADER_KEY:
            return JSONResponse(
                {"detail": "Invalid encrypted_api_key"}, status_code=403
            )

        db_user = (
            db.query(User)
            .filter(
                (User.username == user_model.username)
                | (User.email == user_model.email)
                | (User.phone_number == user_model.phone_number)
            )
            .first()
        )

        if len(user_model.username) < 6:
            return JSONResponse(
                {"detail": "Username must be >= 6 characters"}, status_code=403
            )

        if db_user:
            return JSONResponse(
                {"detail": "Username, email, or phone number already registered"},
                status_code=400,
            )

        new_user = User(
            username=user_model.username,
            email=user_model.email,
            country=user_model.country,
            first_name=user_model.first_name,
            last_name=user_model.last_name,
            gender=user_model.gender,
            date_of_birth=user_model.date_of_birth,
            phone_number=user_model.phone_number,
            password_hash=get_password_hash(user_model.password),
            created_by=user_model.email,
        )

        db.add(new_user)
        db.commit()

        user_activity_model = UserActivity(
            user_id=new_user.id,
            created_by=new_user.email,
        )
        db.add(user_activity_model)
        db.commit()

        return {
            "message": "User created successfully",
            "status_code": status.HTTP_201_CREATED,
        }

    except Exception as error:
        return JSONResponse(
            {"detail": f"An error occurred: {str(error)}"}, status_code=500
        )

    finally:
        if db:
            db.close()


def send_mobile_otp(phone_number: str, otp: str):
    sms_params = {
        "authorization": "",
        "route": "dlt",
        "sender_id": "",
        "variables_values": f"Markwave|{otp}|",
        "message": "",
        "numbers": phone_number,
        "flash": "0",
    }

    response = requests.get(DEV_API_URL, params=sms_params)

    if response.status_code != 200:
        raise Exception(f"SMS sending failed: {response.text}")


@router.get("/")
async def logined_user(db: db_dependency, user: user_dependency):
    try:
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        db_user = (
            db.query(User)
            .filter(
                User.status == "active",
                User.id == user.get("user_id"),
            )
            .first()
        )

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return {
            "message": "Successful",
            "status": status.HTTP_200_OK,
            "user_details": db_user,
        }

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )

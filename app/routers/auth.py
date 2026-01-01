import random
import base64
import logging
from datetime import datetime, timedelta, date
from typing import Annotated, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import jwt
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from fastapi.security.api_key import APIKeyHeader
from app.models import SessionLocal
from app.models.user import User
from app.models.user_activity import UserActivity
from app.utilities.constants import JWT_SECRET_KEY, JWT_ENCODING_ALGORITHM

router = APIRouter(prefix="/auth", tags=["Auth"])

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

API_KEY_NAME = "Authorization"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
encrypted_api_key = Annotated[str, Security(api_key_header)]


class Token(BaseModel):
    access_token: str
    token_type: str


def generate_unique_otp():
    first_digit = random.choice("123456789")
    remaining_digits = random.sample("0123456789".replace(first_digit, ""), 3)
    otp = first_digit + "".join(remaining_digits)
    return otp


def encode_otp(otp):
    today = date.today()
    year = today.year
    month = today.month
    day = today.day
    key = int(year) + int(month) + int(day)
    encypted = (int(otp) + key) % 10000

    return encypted


def encrypt_api_key(api_key: str) -> str:  # bWFya3dhdmU=
    api_key_bytes = api_key.encode("utf-8")
    encrypted_bytes = base64.b64encode(api_key_bytes)
    encrypted_str = encrypted_bytes.decode("utf-8")
    return encrypted_str


def decrypt_api_key(encrypted_api_key: str) -> str:
    try:
        decoded_bytes = base64.b64decode(encrypted_api_key)
        return decoded_bytes.decode("utf-8")
    except Exception as e:
        return None


def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(
    input_value: str, password: str, db: db_dependency
) -> Optional[User]:
    user = (
        db.query(User)
        .filter(
            User.status == "active",
            ((User.email == input_value) | (User.phone_number == input_value)),
        )
        .first()
    )
    if user and bcrypt_context.verify(password, user.password_hash):
        return user
    return False


def create_access_token(
    user_id: int, user_email: str, role: str, expires_delta: Optional[timedelta] = None
) -> str:
    expire = datetime.now() + (
        expires_delta if expires_delta else timedelta(minutes=15)
    )
    to_encode = {
        "user_id": user_id,
        "user_email": user_email,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(to_encode, JWT_SECRET_KEY, JWT_ENCODING_ALGORITHM)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()
):
    global db_user_activity
    try:
        input_value = form_data.username.strip()
        db_user = (
            db.query(User)
            .filter((User.email == input_value) | (User.phone_number == input_value))
            .first()
        )
        if not db_user:
            return JSONResponse(
                {"detail": "INVALID PHONE_NUMBER OR EMAIL"}, status_code=401
            )
        if db_user.status == "inactive":
            return JSONResponse(
                {"detail": "User deactivated his account."}, status_code=401
            )

        user = authenticate_user(input_value, form_data.password.strip(" "), db)
        if db_user:
            db_user_activity = (
                db.query(UserActivity)
                .filter(
                    UserActivity.is_active == True, UserActivity.user_id == db_user.id
                )
                .first()
            )
        if not user:
            if db_user and db_user_activity:
                db_user_activity.login_failed_count += 1
                db_user_activity.last_failed_login = str(datetime.now())
                db.commit()
                db.refresh(db_user_activity)
            return JSONResponse({"detail": "INCORRECT PASSWORD"}, status_code=401)
        token_expires = timedelta(40)
        token = create_access_token(
            user.id, user.email, user.role, expires_delta=token_expires
        )
        if token:
            if db_user_activity:
                db_user_activity.login_success_count += 1
                db_user_activity.last_successful_login = str(datetime.now())
                db.add(db_user_activity)
                db.commit()
                db.refresh(db_user_activity)

            return {
                "access_token": token,
                "token_type": "Bearer",
            }

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),  # Provide error message for debugging
        )

    finally:
        if db:
            db.close()


def get_current_user(
    db: db_dependency, token: str = Depends(oauth2_bearer)
) -> Dict[str, str]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ENCODING_ALGORITHM])
        user_id = payload.get("user_id")
        user_email = payload.get("user_email")
        if not user_email:
            raise get_user_exception()

        if user_id is None:
            user = db.query(User).filter(User.email == user_email).first()
            if not user:
                raise get_user_exception()
            user_id = user.id
        user = (
            db.query(User).filter(User.status == "active", User.id == user_id).first()
        )

        if not user:
            raise get_user_exception()
        return {
            "username": user.username,
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
        }

    except Exception as e:
        raise get_user_exception() from e


def get_user_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

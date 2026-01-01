import base64
from decimal import Decimal
import hashlib
import hmac
import json
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import func
from app.models.booking import Booking
from app.models.customer_profiles import CustomerProfile
from app.models.transaction_history import TransactionHistory
from app.models.user import User
from app.utilities.constants import CASHFREE_API_KEY, CASHFREE_WEBHOOK_SECRET
from cashfree_pg.api_client import Cashfree, CustomerDetails, CreateOrderRequest
from app.routers.users import db_dependency, user_dependency
from sqlalchemy.exc import SQLAlchemyError

Cashfree.XClientId = CASHFREE_API_KEY
Cashfree.XClientSecret = CASHFREE_WEBHOOK_SECRET
Cashfree.XEnvironment = Cashfree.SANDBOX
x_api_version = "2023-08-01"

router = APIRouter(prefix="/cashfree_payment", tags=["payment"])


class CreateOrder(BaseModel):
    orderAmount: float
    phone_number: str


@router.post("/Cashfree/create_booking")
async def create_order(
    user: user_dependency,
    db: db_dependency,
    createorder: CreateOrder,
):
    try:
        if user is None:
            raise HTTPException(
                detail="Not Authenticated", status_code=status.HTTP_401_UNAUTHORIZED
            )

        user_info = (
            db.query(User)
            .filter(User.is_active == True, User.id == user.get("user_id"))
            .first()
        )

        tags = {
            "user_id": str(user_info.id),
        }
        customer_details = CustomerDetails(
            customer_id="customer_" + str(user_info.id),
            customer_name=user_info.username,
            customer_phone=createorder.phone_number,
            customer_email=user_info.email,
        )
        createOrderRequest = CreateOrderRequest(
            order_amount=createorder.orderAmount,
            order_currency="INR",
            customer_details=customer_details,
            order_tags=tags,
        )

        api_response = Cashfree().PGCreateOrder(
            x_api_version, createOrderRequest, None, None
        )
        return api_response.data
    except Exception as e:
        return JSONResponse(
            {"detail": "error in creating session", "error": str(e)}, status_code=500
        )

    finally:
        if db:
            db.close()


def generateSignature(payload, timestamp, signature_2):
    signatureData = timestamp + payload

    message = bytes(signatureData, "utf-8")
    secretkey = bytes(Cashfree.XClientSecret, "utf-8")
    signature = base64.b64encode(
        hmac.new(secretkey, message, digestmod=hashlib.sha256).digest()
    )
    computed_signature = str(signature, encoding="utf-8")

    return computed_signature == signature_2


def get_next_txn_no(db: db_dependency):

    max_txn_no = db.query(func.max(TransactionHistory.txn_no)).scalar()
    return max_txn_no + 1 if max_txn_no else 10001


@router.post("/webhook")
async def disp(request: Request, db: db_dependency):

    try:
        raw_body = await request.body()

        timestamp = request.headers.get("x-webhook-timestamp")
        signature = request.headers.get("x-webhook-signature")
        decoded_body = raw_body.decode("utf-8")

        if generateSignature(decoded_body, timestamp, signature):

            body_json = json.loads(decoded_body)

            customer_details = body_json["data"]["customer_details"]
            payment_details = body_json["data"]["payment"]
            order_details = body_json["data"]["order"]
            order_tags = order_details["order_tags"]
            payment_gateway_details = body_json["data"]["payment_gateway_details"]

            customer_name = customer_details["customer_name"]
            customer_email = customer_details["customer_email"]
            customer_phone_number = customer_details["customer_phone"]
            user_id = order_tags["user_id"]
            order_id = order_details["order_id"]

            payment_id = payment_details["cf_payment_id"]
            payment_status = payment_details["payment_status"]
            amount = payment_details["payment_amount"]
            payment_method = payment_details["payment_method"]
            transaction_time = body_json["data"]["payment"]["payment_time"]

            user_details = (
                db.query(User)
                .filter(User.is_active == True, User.id == int(user_id))
                .first()
            )

            txn_number = get_next_txn_no(db)

            if payment_status == "SUCCESS":
                new_order = Booking(
                    user_id=user_id,
                    txn_no=txn_number,
                    cost=amount,
                    created_by=user_details.email,
                    mobile_number=customer_phone_number,
                    status=payment_status,
                )
                db.add(new_order)
                db.commit()
            new_transaction = TransactionHistory(
                payment_method_type="CASHFREE",
                user_id=user_id,
                txn_no=txn_number,
                currency="INR",
                price=amount,
                transaction_time=transaction_time,
                customer_phone_number=customer_phone_number,
                customer_name=customer_name,
                customer_email=customer_email,
                payment_method=payment_method,
                payment_id=payment_id,
                created_by=user_details.email,
                payment_status=payment_status,
            )
            db.add(new_transaction)
            db.commit()

            customer_profile = (
                db.query(CustomerProfile)
                .filter(CustomerProfile.user_id == int(user_id))
                .first()
            )
            paid_amount = Decimal(str(amount))

            if paid_amount >= 10000:
                customer_profile.qualifying_trips_count += 1
                customer_profile.total_qualifying_amount += paid_amount

                customer_profile.free_trip_earned_count = (
                    customer_profile.qualifying_trips_count // 6
                )

            db.commit()
    except SQLAlchemyError as db_error:
        db.rollback()
        return JSONResponse(
            {"error_code": "db_error", "message": str(db_error)}, status_code=500
        )

    except Exception as e:
        return JSONResponse(
            {
                "error_code": "webhook_error",
                "message": "Technical error occurred while processing Cashfree webhook.",
            },
            status_code=500,
        )

    finally:
        if db:
            db.close()

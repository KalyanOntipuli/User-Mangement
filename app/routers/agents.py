from fastapi import APIRouter, HTTPException, status
from typing import Optional
from app.models.customer_profiles import CustomerProfile
from app.models.user import User
from app.routers.users import user_dependency, db_dependency
from app.models.agent_customer import AgentCustomer
from app.utilities.constants import ADMIN_ACCESS_EMAILS
from app.validator.customers_response_details import CustomerResponseDetails


router = APIRouter(prefix="/agent", tags=["Agent"])


@router.get("/get_assigned_customers")
async def get_assigned_customers(
    db: db_dependency,
    user: user_dependency,
    sort_by: Optional[int] = None,
    page: int = 1,
    size: int = 20,
):
    try:
        print(user)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not Authenticated",
            )

        if user.get("role") != "agent":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ONLY AGENT CAN ACCESS THIS API",
            )

        if sort_by not in (None, 1, 2):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="sort_by must be 1 (asc) or 2 (desc)",
            )

        page = max(page - 1, 0)
        agent_id = user.get("user_id")

        query = (
            db.query(User, CustomerProfile)
            .join(
                AgentCustomer,
                AgentCustomer.customer_id == User.id,
            )
            .outerjoin(
                CustomerProfile,
                CustomerProfile.user_id == User.id,
            )
            .filter(
                AgentCustomer.agent_id == agent_id,
                User.role == "customer",
                User.status == "active",
            )
        )

        if sort_by == 1:
            query = query.order_by(User.id.asc())
        elif sort_by == 2:
            query = query.order_by(User.id.desc())

        total_items = query.count()
        total_pages = (total_items + size - 1) // size

        rows = query.offset(page * size).limit(size).all()

        data = []
        for user_obj, customer_obj in rows:
            data.append(
                CustomerResponseDetails(
                    id=user_obj.id,
                    username=user_obj.username,
                    email=user_obj.email,
                    phone_number=user_obj.phone_number,
                    first_name=user_obj.first_name,
                    last_name=user_obj.last_name,
                    gender=user_obj.gender,
                    date_of_birth=user_obj.date_of_birth,
                    role=user_obj.role,
                    status=user_obj.status,
                    country=user_obj.country,
                    state=user_obj.state,
                    city_of_residence=user_obj.city_of_residence,
                    created_date=user_obj.created_date,
                    passport_no=customer_obj.passport_no if customer_obj else None,
                    passport_expiry_date=(
                        customer_obj.passport_expiry_date if customer_obj else None
                    ),
                    passport_issuing_country=(
                        customer_obj.passport_issuing_country if customer_obj else None
                    ),
                    pancard_number=(
                        customer_obj.pancard_number if customer_obj else None
                    ),
                    emergency_contact=(
                        customer_obj.emergency_contact if customer_obj else None
                    ),
                    preferred_language=(
                        customer_obj.preferred_language if customer_obj else None
                    ),
                )
            )

        return {
            "message": "SUCCESS",
            "status": 200,
            "data": data,
            "pagination": {
                "current_page": page + 1,
                "items_per_page": size,
                "total_pages": total_pages,
                "total_items": total_items,
            },
        }

    except Exception as error:
        raise HTTPException(
            detail=str(error),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

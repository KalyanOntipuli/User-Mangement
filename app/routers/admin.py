from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.infra.notifications import notification_for_agent_to_send_credentials
from app.models.agent_customer import AgentCustomer
from app.models.agent_profile import AgentProfile
from app.models.customer_profiles import CustomerProfile
from app.models.user_activity import UserActivity
from app.models.user import User
from app.routers.users import db_dependency, user_dependency
from app.routers.auth import decrypt_api_key, encrypted_api_key, get_password_hash
from app.utilities.constants import ADMIN_ACCESS_EMAILS, AUTHORIZATION_HEADER_KEY
from app.validator.agent_response_details import AgentDetailResponse
from app.validator.create_agent_request import CreateAgentRequest

from app.validator.customers_response_details import CustomerResponseDetails
from app.validator.user_validator import UserModel
from starlette import status
from fastapi import BackgroundTasks

router = APIRouter(prefix="/admin", tags=["Admin"])


class AssignCustomerRequest(BaseModel):
    agent_id: int
    customer_id: int


@router.post("/create_agent", status_code=status.HTTP_201_CREATED)
async def create_new_agent(
    background_tasks: BackgroundTasks,
    user: user_dependency,
    db: db_dependency,
    payload: CreateAgentRequest,
):
    try:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )

        if user.get("role") != "admin" or user.get("email") not in ADMIN_ACCESS_EMAILS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can create agents",
            )

        existing_user = (
            db.query(User)
            .filter(
                (User.username == payload.username)
                | (User.email == payload.email)
                | (User.phone_number == payload.phone_number)
            )
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username, email, or phone number already exists",
            )
        new_user = User(
            username=payload.username,
            first_name = payload.first_name,
            last_name = payload.last_name,
            email=payload.email,
            phone_number=payload.phone_number,
            gender = payload.gender,
            password_hash=get_password_hash(payload.password),
            role="agent",
            created_by=user.get("email"),
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        agent_profile = AgentProfile(
            user_id=new_user.id,
            agent_code=f"markwave-agent-{new_user.id}",
            commission_percentage=payload.commission_percentage,
            assigned_region=payload.assigned_region,
            kyc_status="pending",
        )

        db.add(agent_profile)
        db.commit()

        background_tasks.add_task(
            notification_for_agent_to_send_credentials,
            payload.username,
            "markwave",
            payload.email,
            payload.password,
        )

        return {
            "message": "Agent created successfully",
            "agent_id": new_user.id,
        }
    except Exception as error:
        raise HTTPException(
            detail=str(error), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/get_all_agents")
async def get_all_agents(
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
                detail="Not authenticated",
            )

        if user.get("email") not in ADMIN_ACCESS_EMAILS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin has access",
            )

        page = max(page - 1, 0)

        query = (
            db.query(User, AgentProfile)
            .join(AgentProfile, AgentProfile.user_id == User.id)
            .filter(
                User.role == "agent",
                User.status == "active",
            )
        )
        if sort_by not in (None, 1, 2):
            raise HTTPException(
                status_code=400,
                detail="sort_by must be 1 (asc) or 2 (desc)",
            )

        if sort_by == 1:
            query = query.order_by(User.id.asc())
        elif sort_by == 2:
            query = query.order_by(User.id.desc())

        total_items = query.count()
        total_pages = (total_items + size - 1) // size

        rows = query.offset(page * size).limit(size).all()

        data = []
        for user_obj, agent_obj in rows:
            data.append(
                AgentDetailResponse(
                    id=user_obj.id,
                    username=user_obj.username,
                    email=user_obj.email,
                    phone_number=user_obj.phone_number,
                    first_name=user_obj.first_name,
                    last_name=user_obj.last_name,
                    role=user_obj.role,
                    status=user_obj.status,
                    country=user_obj.country,
                    state=user_obj.state,
                    city_of_residence=user_obj.city_of_residence,
                    created_date=user_obj.created_date,
                    agent_code=agent_obj.agent_code,
                    commission_percentage=float(agent_obj.commission_percentage),
                    assigned_region=agent_obj.assigned_region,
                    kyc_status=agent_obj.kyc_status,
                    is_active=agent_obj.is_active,
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
            detail=str(error), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/get_all_customers")
async def get_all_customers(
    db: db_dependency,
    user: user_dependency,
    sort_by: Optional[int] = None,
    page: int = 1,
    size: int = 20,
):
    try:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not Authenticated",
            )

        if user.get("email") not in ADMIN_ACCESS_EMAILS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ONLY ADMIN HAVE ACCESS TO THIS API",
            )

        if sort_by not in (None, 1, 2):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="sort_by must be 1 (asc) or 2 (desc)",
            )

        page = max(page - 1, 0)

        query = (
            db.query(User, CustomerProfile)
            .outerjoin(CustomerProfile, CustomerProfile.user_id == User.id)
            .filter(
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
                    nationality=user_obj.nationality,
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
            detail=str(error), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/get_agent_details_by_id/{id}")
async def get_agent_details_by_id(
    id: int,
    db: db_dependency,
    user: user_dependency,
):
    try:

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not Authenticated",
            )

        if user.get("email") not in ADMIN_ACCESS_EMAILS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ONLY ADMIN HAVE ACCESS TO THIS API",
            )

        result = (
            db.query(User, AgentProfile)
            .join(AgentProfile, AgentProfile.user_id == User.id)
            .filter(
                User.id == id,
                User.role == "agent",
                User.status == "active",
            )
            .first()
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found",
            )

        user_obj, agent_obj = result
        return {
            "message": "SUCCESSFUL",
            "status": 200,
            "data": AgentDetailResponse(
                id=user_obj.id,
                username=user_obj.username,
                email=user_obj.email,
                phone_number=user_obj.phone_number,
                first_name=user_obj.first_name,
                last_name=user_obj.last_name,
                role=user_obj.role,
                status=user_obj.status,
                country=user_obj.country,
                state=user_obj.state,
                city_of_residence=user_obj.city_of_residence,
                created_date=user_obj.created_date,
                agent_code=agent_obj.agent_code,
                commission_percentage=float(agent_obj.commission_percentage),
                assigned_region=agent_obj.assigned_region,
                kyc_status=agent_obj.kyc_status,
                is_active=agent_obj.is_active,
            ),
        }
    except Exception as error:
        raise HTTPException(
            detail=str(error), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/get_customer_details_by_id/{id}")
async def get_customer_details_by_id(
    id: int,
    db: db_dependency,
    user: user_dependency,
):
    try:

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not Authenticated",
            )

        if user.get("email") not in ADMIN_ACCESS_EMAILS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ONLY ADMIN HAVE ACCESS TO THIS API",
            )
        result = (
            db.query(User, CustomerProfile)
            .outerjoin(CustomerProfile, CustomerProfile.user_id == User.id)
            .filter(
                User.id == id,
                User.role == "customer",
                User.status == "active",
            )
            .first()
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found",
            )

        user_obj, customer_obj = result

        return {
            "message": "SUCCESSFUL",
            "status": 200,
            "data": CustomerResponseDetails(
                id=user_obj.id,
                username=user_obj.username,
                email=user_obj.email,
                phone_number=user_obj.phone_number,
                first_name=user_obj.first_name,
                last_name=user_obj.last_name,
                role=user_obj.role,
                gender=user_obj.gender,
                date_of_birth=user_obj.date_of_birth,
                status=user_obj.status,
                nationality=user_obj.nationality,
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
                pancard_number=customer_obj.pancard_number if customer_obj else None,
                emergency_contact=(
                    customer_obj.emergency_contact if customer_obj else None
                ),
                preferred_language=(
                    customer_obj.preferred_language if customer_obj else None
                ),
            ),
        }
    except Exception as error:
        raise HTTPException(
            detail=str(error), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/assign-customer-to-agent")
async def assign_customer_to_agent(
    payload: AssignCustomerRequest,
    db: db_dependency,
    user: user_dependency,
):
    try:

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )

        if user.get("role") != "admin" and user.get("email") not in ADMIN_ACCESS_EMAILS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can assign customers to agents",
            )

        agent = (
            db.query(User)
            .filter(
                User.id == payload.agent_id,
                User.role == "agent",
                User.status == "active",
            )
            .first()
        )

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found or inactive",
            )

        customer = (
            db.query(User)
            .filter(
                User.id == payload.customer_id,
                User.role == "customer",
                User.status == "active",
            )
            .first()
        )

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found or inactive",
            )

        existing_assignment = (
            db.query(AgentCustomer)
            .filter(AgentCustomer.customer_id == payload.customer_id)
            .first()
        )

        if existing_assignment:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Customer is already assigned to an agent",
            )

        assignment = AgentCustomer(
            agent_id=payload.agent_id,
            customer_id=payload.customer_id,
        )

        db.add(assignment)
        db.commit()

        return {
            "message": "Customer successfully assigned to agent",
            "agent_id": payload.agent_id,
            "customer_id": payload.customer_id,
        }
    except Exception as error:
        raise HTTPException(
            detail=str(error), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

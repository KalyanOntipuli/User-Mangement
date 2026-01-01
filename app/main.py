from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.models import Base, engine
from app.models import * 
from app.routers import auth, cashfree_payment, users, admin, agents
import warnings

warnings.filterwarnings(
    "ignore",
    message=".*constr.*deprecated.*",
)

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(cashfree_payment.router)
app.include_router(agents.router)


origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

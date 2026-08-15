from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
import models

from routers.employee import router as employee_router
from routers.user import router as user_router
from routers.department import router as department_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agar Alembic use kar rahe ho to is line ko baad me remove kar dena
Base.metadata.create_all(bind=engine)

app.include_router(user_router)
app.include_router(employee_router)
app.include_router(department_router)
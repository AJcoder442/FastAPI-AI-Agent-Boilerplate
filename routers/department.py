from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import DepartmentCreate, DepartmentResponse
from services import department_service
from security import get_current_user, required_admin
from models import User

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return department_service.create_department(department, db)

@router.get("", response_model=list[DepartmentResponse])
def get_all_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return department_service.get_all_departments(db)

@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return department_service.get_department(department_id, db)

@router.delete("/{department_id}", status_code=status.HTTP_200_OK)
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(required_admin)
):
    return department_service.delete_department(department_id, db)

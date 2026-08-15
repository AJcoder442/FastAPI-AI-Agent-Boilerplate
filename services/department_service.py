from sqlalchemy import select
from sqlalchemy.orm import Session
from models import Department
from schemas import DepartmentCreate
from fastapi import HTTPException, status

def create_department(department: DepartmentCreate, db: Session):
    existing = db.scalar(select(Department).where(Department.name == department.name))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department already exists"
        )
    
    db_dept = Department(name=department.name)
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept

def get_department(department_id: int, db: Session):
    dept = db.get(Department, department_id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    return dept

def get_all_departments(db: Session):
    return db.scalars(select(Department)).all()

def delete_department(department_id: int, db: Session):
    dept = db.get(Department, department_id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    if dept.employees:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete department with existing employees"
        )
    
    db.delete(dept)
    db.commit()
    return {"message": "Department successfully deleted"}

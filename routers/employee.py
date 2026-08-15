from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Employee
from schemas import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from services import employee_service
from fastapi import status
from security import get_current_user,required_admin
from models import User

router=APIRouter()



@router.get("/employee/{employee_id}")
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return employee_service.get_employee(employee_id, db)



  
@router.post("/employee",response_model=EmployeeResponse,status_code=status.HTTP_201_CREATED,)
def create_employee(
    employee:EmployeeCreate,
    
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
  return employee_service.create_employee(employee, db)
   

        
@router.get("/employees")
def get_all_employee(
   department:str | None=None,
    name : str |None=None,
    min_salary: float |None=None,
    max_salary: float |None=None,
    page: int=1,
    limit: int =10,
    sort_by:str |None= None,
    order: str = "asc",
    db: Session=Depends(get_db),
    current_user: User=Depends(get_current_user)
):
    return employee_service.get_all_employee(department,name,min_salary,max_salary,page,limit,sort_by,order,db)



    
@router.put("/employee/{employee_id}")
def update_employee(
    employee_id:int,
    employee:EmployeeUpdate,
    db:Session=Depends(get_db),
    current_user: User = Depends(get_current_user)
):return employee_service.update_employee(employee_id,employee,db)

   
@router.delete("/employee/{employee_id}")
def delete_employee(
    employee_id:int,
    db:Session=Depends(get_db),
    admin: User = Depends(required_admin)

): return employee_service.delete_employee(employee_id,db)
   
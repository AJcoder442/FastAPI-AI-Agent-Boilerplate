
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, contains_eager
from models import Employee, Department
from schemas import EmployeeCreate, EmployeeUpdate
from fastapi import HTTPException


def get_employee(employee_id:int,db: Session):

       employee= db.get(Employee,employee_id)
       if  not employee:
          return {"message":"employee not found"} 
       
       return employee
    


def create_employee(employee:EmployeeCreate, db:Session):
       db_employee=Employee(
            **employee.model_dump()
       )
       db.add(db_employee)
       db.commit()
       db.refresh(db_employee)

       return db_employee
   

def update_employee(employee_id : int,update_employee : EmployeeUpdate, db:Session):

      employee=db.get(Employee,employee_id)
      if not employee:
           raise HTTPException(
                status_code=404,
                detail="Employee not Found"
           )
        
      employee.name=update_employee.name
      employee.email=update_employee.email
      employee.salary=update_employee.salary
      employee.joining_date=update_employee.joining_date
      employee.is_active=update_employee.is_active
      employee.department_id=update_employee.department_id

      db.commit()
      db.refresh(employee)
      return employee
 

def delete_employee(employee_id: int,db:Session):
 
      employee=db.get(Employee,employee_id)
      if not employee:
            raise HTTPException(
                status_code=404,
                detail="Employee not Found"
           )
           
         
      db.delete(employee)
      db.commit()
      
      return {
         "message":" Employee was successfully deleted"
      }    
 
def get_all_employee(department: str|None,Name: str |None ,min_salary:float|None,max_salary:float|None, page :int,limit:int,sort_by :str |None,order:str,db:Session):
      sort_columns={
           "name": Employee.name,
           "salary": Employee.salary,
           "joining_date":Employee.joining_date,
           "department":Department.name
      }
      
      query=select(Employee)
      
      if department or sort_by == "department":
           query=query.join(Employee.department).options(contains_eager(Employee.department))
      else:
           query=query.options(joinedload(Employee.department))
      
      if department:
           query=query.where(Department.name==department)

      if Name:
           query=query.where(Employee.name.ilike(f"%{Name}%")) #searching

      if min_salary is not None:
           query=query.where(
                Employee.salary>=min_salary
            
           )   
      if max_salary is not None:
           query=query.where(
                
                Employee.salary<= max_salary
              )
           
      if sort_by:
           column=sort_columns.get(sort_by)

           if column is None:
                raise HTTPException(
                     status_code=400,
                     detail="Invalid sort column"
                )
           
           if order=="desc":
               query=query.order_by(column.desc())

           else:
               query=query.order_by(column.asc())
    
      offset= (page-1)*limit
      query=query.offset(offset)
      query=query.limit(limit)

      employees=db.scalars(query).all()

      return employees
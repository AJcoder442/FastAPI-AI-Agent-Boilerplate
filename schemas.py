from pydantic import BaseModel,EmailStr,ConfigDict
from datetime import date

class DepartmentCreate(BaseModel):
    name: str

class DepartmentResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class EmployeeCreate(BaseModel):
    name: str
    email: str
    salary: float
    joining_date: date
    is_active: bool
    department_id: int


class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: str
    salary: float
    joining_date: date
    is_active: bool
    department_id: int
    department: DepartmentResponse | None = None

    model_config = {
        "from_attributes": True
    }

class EmployeeUpdate(BaseModel):
    name: str
    email: str
    salary: float
    joining_date: date
    is_active: bool
    department_id: int

class UserCreate(BaseModel):
    username:str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool

    model_config=ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str
    
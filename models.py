from sqlalchemy import Integer,String,Boolean,Date,Numeric,ForeignKey,DateTime
from sqlalchemy.orm import Mapped,mapped_column,relationship
from database import Base
from datetime import date, datetime, timezone

class Employee(Base):
    __tablename__="employees"

    id:Mapped[int]=mapped_column( Integer,primary_key=True)
    name: Mapped[str]=mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))
    salary:Mapped[float]= mapped_column(Numeric)
    joining_date: Mapped[date]= mapped_column(Date)
    is_active: Mapped[bool]=mapped_column(Boolean)
    department_id: Mapped[int] =mapped_column( ForeignKey("departments.id"))
    department: Mapped["Department"]=relationship(back_populates="employees")

class User(Base):
    __tablename__="users"

    id:Mapped[int]= mapped_column(primary_key=True)
    username: Mapped[str]=mapped_column(String(100),unique=True)
    email:Mapped[str]= mapped_column(String(100),unique=True)
    hashed_password: Mapped[str]=mapped_column(String(255))
    is_active: Mapped[bool]=mapped_column(Boolean,default=True)
    role: Mapped[str] = mapped_column( String(20),default="user")

class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    employees: Mapped[list["Employee"]]=relationship(back_populates="department")

class RefreshSession(Base):
    __tablename__ = "refresh_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    refresh_token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship()



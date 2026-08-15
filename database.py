# from sqlalchemy import create_engine
# from sqlalchemy.orm import DeclarativeBase ,sessionmaker 


# database_url="postgresql+pyscopg://postgres:python@localhost:5432/company_db"

# engine=create_engine(database_url)

# sessionlocal=sessionmaker(

#     autocommit=False,
#     autoflush=False,
#     bind=engine
# )

# def get_db():
#     db=sessionlocal()
#     try:
#         yield db

#     finally:
#         db.close()
        
# class Base(DeclarativeBase):
#     pass
# # from sqlalchemy import create_engine

# # database_url = "postgresql+pyscopg://postgres:python@localhost:5432/company_db"

# # print("repr :", repr(database_url))
# # print("bytes:", list(database_url.encode()))

# # engine = create_engine(database_url)

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import settings

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Base(DeclarativeBase):
    pass
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from main import app
from database import Base, get_db
from models import User
from security import hash_password

# 1. Dynamically verify and create test_company_db in PostgreSQL
POSTGRES_SERVER_URL = "postgresql+psycopg://postgres:python@localhost:5432/postgres"
TEST_DATABASE_URL = "postgresql+psycopg://postgres:python@localhost:5432/test_company_db"

def setup_test_database():
    # Connect to the default 'postgres' database to create the test database if missing
    engine_default = create_engine(POSTGRES_SERVER_URL, isolation_level="AUTOCOMMIT")
    with engine_default.connect() as conn:
        exists = conn.execute(text("SELECT 1 FROM pg_database WHERE datname='test_company_db'")).scalar()
        if not exists:
            conn.execute(text("CREATE DATABASE test_company_db"))
    engine_default.dispose()

setup_test_database()

# 2. Setup SQLAlchemy Engine and Session for test database
engine_test = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

@pytest.fixture(name="db")
def fixture_db():
    # Drop and recreate schema on test database for clean state per test
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine_test)

@pytest.fixture(name="client")
def fixture_client(db):
    # Override get_db dependency to yield the test database session
    def override_get_db():
        try:
            yield db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(name="auth_headers")
def fixture_auth_headers(client, db):
    # Pre-register a test user
    username = "testuser"
    email = "testuser@example.com"
    password = "testpassword123"
    
    hashed = hash_password(password)
    user = User(username=username, email=email, hashed_password=hashed, role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Login to obtain headers
    response = client.post("/users/login", data={"username": email, "password": password})
    assert response.status_code == 200
    token_data = response.json()
    token = token_data["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(name="admin_headers")
def fixture_admin_headers(client, db):
    # Pre-register an admin user
    username = "adminuser"
    email = "adminuser@example.com"
    password = "adminpassword123"
    
    hashed = hash_password(password)
    user = User(username=username, email=email, hashed_password=hashed, role="admin")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Login to obtain headers
    response = client.post("/users/login", data={"username": email, "password": password})
    assert response.status_code == 200
    token_data = response.json()
    token = token_data["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

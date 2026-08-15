# Cloud-Native FastAPI Employee & Department Management API

A robust, enterprise-ready REST API built with **FastAPI** and **Python**, featuring secure OAuth2 (JWT) authentication, automated database migrations, unit testing, and a fully automated cloud deployment pipeline.

This project is packaged with **Docker** and deployed serverless using **AWS ECS Fargate** and **AWS ECR** via **GitHub Actions** CI/CD.

---

## 🚀 Key Features

* **Secure Authentication**: User signup, login, and token-based authentication using **OAuth2 (JWT Tokens)**, with secure password hashing (`bcrypt`).
* **Employee Directory**: Full CRUD endpoints to manage employees (join dates, roles, salaries, contact details).
* **Department Hierarchy**: Manage departments, track employee assignments, and aggregate department stats.
* **Database & ORM**: **SQLAlchemy 2.0** with **Alembic** migrations for structured PostgreSQL interactions.
* **Quality Assurance**: 100% automated test suite using **Pytest** and **HTTPX** for API client testing.
* **Dockerized Environment**: Easily run the entire stack locally or in production via lightweight containerization.
* **CI/CD Pipeline**: GitHub Actions automatically spins up a PostgreSQL container, runs tests, builds the Docker image, pushes it to **AWS ECR**, and deploys to **AWS ECS Fargate**.

---

## 🛠️ Tech Stack & Architecture

* **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
* **Database**: [PostgreSQL](https://www.postgresql.org/)
* **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
* **Database Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
* **Containerization**: [Docker](https://www.docker.com/) & Docker Compose
* **Cloud Infrastructure**: AWS (ECR, ECS Fargate, IAM, Security Groups)
* **CI/CD**: GitHub Actions
* **Testing**: Pytest & HTTPX

---

## ⚙️ Local Setup Guide

### 1. Clone the Repository
```bash
git clone https://github.com/AJcoder442/FastAPI-AI-Agent-Boilerplate.git
cd FastAPI-AI-Agent-Boilerplate
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql+psycopg://postgres:yourpassword@localhost:5432/postgres
SECRET_KEY=generate-a-strong-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. Run Locally with Virtual Environment
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start the development server
uvicorn main:app --reload --port 8000
```
Visit `http://localhost:8000/docs` to access the interactive API documentation.

### 4. Run with Docker
```bash
# Build and run using Docker
docker build -t fastapi-app .
docker run -p 8000:8000 --env-file .env fastapi-app
```

---

## 🧪 Testing

The project uses **Pytest** for testing API endpoints. To run tests locally:
```bash
pytest -v
```

---

## ☁️ Continuous Deployment to AWS

Any push to the `main` branch triggers the GitHub Actions workflow (`deploy.yml`):
1. **Lint & Test**: Starts a containerized PostgreSQL database and runs all unit tests.
2. **Build Docker Image**: Builds the application container.
3. **Publish**: Pushes the image to **AWS Elastic Container Registry (ECR)**.
4. **Deploy**: Refreshes the **AWS ECS Fargate** service to download and spin up the new image.

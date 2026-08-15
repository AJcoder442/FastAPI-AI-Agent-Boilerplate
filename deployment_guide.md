# AWS ECS Deployment Guide (Cloud Build)

This guide walks you through setting up **AWS ECS (Elastic Container Service)** and **GitHub Actions** so that you can deploy your FastAPI container directly from GitHub. 

By using this approach, **you do not need to install Docker locally** or use any laptop storage. GitHub Actions will build the Docker image in the cloud and push it to AWS for execution.

---

## Architecture Overview

1. **GitHub Actions**: Runs your test suite on every push to `main`. If they pass, it builds your Docker image on GitHub's servers and pushes it to AWS.
2. **AWS ECR (Elastic Container Registry)**: Stores your Docker images in the cloud.
3. **AWS ECS Fargate**: Runs your container serverless (without managing virtual machines).
4. **PostgreSQL**: You can use a managed database like **AWS RDS PostgreSQL** in production.

---

## Step 1: Create an ECR Repository on AWS
1. Open the **AWS Console** and search for **Elastic Container Registry (ECR)**.
2. Click **Create Repository**.
3. Choose **Private** and name your repository (e.g., `company-api`).
4. Click **Create Repository** and copy the URI (e.g., `123456789012.dkr.ecr.us-east-1.amazonaws.com/company-api`).

---

## Step 2: Set up AWS ECS (Elastic Container Service)

### A. Create an ECS Cluster
1. Search for **ECS** in the AWS Console.
2. Click **Clusters** -> **Create Cluster**.
3. Name your cluster (e.g., `company-cluster`).
4. Under Infrastructure, check **AWS Fargate (serverless)**.
5. Click **Create**.

### B. Create an IAM Execution Role (if you don't have one)
ECS needs permission to pull images from ECR and send logs to CloudWatch.
1. AWS usually creates a default role named `ecsTaskExecutionRole` automatically. Verify this exists in the IAM console, or let ECS create it for you during the Task Definition step.

### C. Create a Task Definition
A Task Definition is the blueprint for your container.
1. In the ECS Console, click **Task Definitions** -> **Create new task definition** (select **Create new task definition with JSON** or use the UI).
2. Set **Task definition family** (e.g., `company-api-task`).
3. Select Launch type: **AWS Fargate**.
4. Operating system: **Linux/x86_64**.
5. Task size (to save money on Free Tier / low cost):
   * **vCPU**: `0.25 vCPU`
   * **Memory**: `0.5 GB`
6. Under **Container - 1**:
   * **Name**: `web` (This must match your GitHub Secrets!)
   * **Image URI**: Enter your ECR repository URI with `:latest` (e.g., `123456789012.dkr.ecr.us-east-1.amazonaws.com/company-api:latest`).
   * **Port mappings**: Container port `8000`, Protocol `TCP`, App protocol `HTTP`.
7. Under Environment variables, configure your production settings (e.g., `DATABASE_URL` pointing to your AWS RDS instance, `SECRET_KEY`, etc.).
8. Click **Create**.

### D. Create an ECS Service
A Service keeps a specified number of task definitions running.
1. Go back to your **ECS Cluster** -> **Services** tab -> **Create**.
2. Deployment configuration:
   * Application type: **Service**.
   * Task Definition Family: select `company-api-task`, Revision: `Latest`.
   * Service name: `company-service`.
   * Desired tasks: `1` (or more).
3. Networking:
   * Choose your VPC and subnets.
   * **Security Group**: Allow inbound traffic on port **`8000`** (to access the FastAPI app) and port `5432` if database is external.
   * Public IP: **Turn ON** (needed to access it from the internet).
4. Click **Create**.

---

## Step 3: Setup GitHub Secrets

To allow GitHub Actions to build and deploy your code, add your AWS credentials as secrets in your GitHub repository:

1. Open your repository on GitHub.
2. Go to **Settings** -> **Secrets and variables** -> **Actions** -> Click **New repository secret**.
3. Add the following secrets:

| Secret Name | Value Example / Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | Your AWS IAM User Access Key |
| `AWS_SECRET_ACCESS_KEY` | Your AWS IAM User Secret Access Key |
| `AWS_REGION` | `us-east-1` (or the region where your services are created) |
| `ECR_REPOSITORY` | `company-api` (the name of your ECR repository) |
| `ECS_CLUSTER` | `company-cluster` (the name of your ECS cluster) |
| `ECS_SERVICE` | `company-service` (the name of your ECS service) |
| `ECS_CONTAINER_NAME` | `web` (the name of the container inside your Task Definition) |
| `ECS_TASK_DEFINITION_FAMILY` | `company-api-task` (the family name of your Task Definition) |

---

## Step 4: Trigger the Deployment!

1. Commit all your changes locally:
   ```bash
   git add .
   git commit -m "Configure Docker and GitHub Actions CI/CD"
   ```
2. Push your changes to the `main` branch:
   ```bash
   git push origin main
   ```
3. Go to the **Actions** tab in your GitHub repository.
4. You will see the **Deploy to AWS ECS** workflow running. It will:
   * Spin up a temporary PostgreSQL service.
   * Run your `pytest` suite.
   * Build the Docker image and push it to AWS ECR.
   * Refresh your ECS service with the new build.

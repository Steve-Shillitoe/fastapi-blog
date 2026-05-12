# A FastAPI Blogging Web Application
This web application is built with the Python **FastApi Framework** and it allows users to enter, update & delete blog posts.  It is publically available at **https://fastapiblog.net**

**Jinja2 templates** are used to create an HTML frontend for the backend API JSON endpoints. 
**Template inheritance** with a layout file is utilised to simplify the template files. 
Additionally, **Bootstrap** is used for styling. Consequently, the application is configured to use static files for CSS and images.

**Pydantic schemas** are used to validate API requests and responses in FastAPI. **Pydantic schemas** define the API contract - what data goes in and what comes out - and **FastAPI** uses them for validation, serialization, and automatic documentation. Consequently this project contains a schemas file with request and response models, 
that have field validations for minimum and maximum length for strings. 

This project uses **SQLAlchemy 2.0** as the ORM to manage database interactions with a local **SQLite** database. SQLAlchemy provides a clean separation between application logic and persistence by mapping Python classes to database tables using declarative models. The ```engine``` establishes the database connection, ```SessionLocal``` manages transactional sessions, and the declarative ```Base``` class allows models to inherit consistent metadata. This approach ensures type safety, maintainable schema definitions, and database-agnostic flexibility should the project later migrate from SQLite to PostgreSQL or another production-grade database.

## Setting up the application for development
### Dependency Management with uv
This project uses **uv** instead of **pip** for dependency management, 
providing faster installs, lockfile-based reproducibility, 
and consistent environments across development, CI, and production.
#### Create the project
In Windows PowerShell,
```
uv init fastapi_blog
cd fastapi_blog
```
Install **FastAPI**
```
uv add "fastapi[standard]"
```
This gives us
**Core runtime**
  - FastAPI – the framework itself
  - Starlette – ASGI framework (routing, middleware, websockets, background tasks)
  - Pydantic – data validation, settings, schemas
**Web Server**
  - uvicorn (ASGI server)

To open Visual Studio Code in the project directory,
```
code .
```
### To run fastapi_blog from Visual Studio Code
**uv** initialises the project with a **main.py** file. 
Assuming **main.py** contains executable code, open a terminal in Visual Studio code and launch the web application using the command
```
uv fastapi run dev main.py
```
**dev** mode gives us automatic reload of the web server when code is changed.
Open a browser window with the url **localhost:8000** to view the web application.
Or use,
```
uv run uvicorn main:app --reload
```
This guarantees it runs inside uv’s managed environment.

## Switching from SQLite to PostgreSQL (Development Setup)

This project originally used **SQLite** for local development, but has been migrated to **PostgreSQL** for improved performance and production readiness. **Alembic** is used to manage database migrations, and async SQLAlchemy with ```asyncpg``` ensures efficient asynchronous database operations. The steps below guide developers to set up their development environment so it mirrors production best practices.

### Step-by-Step Setup

1. **Install PostgreSQL** on your machine.

2. **Create a development database**, e.g., ```blogdb``.

3. **Update connection strings**:

- database.py →
```
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://<username>:<password>@<host>:<port>/blogdb"
```

- ```alembic.ini``` → set the same URL under ```sqlalchemy.url```.

4. **Install Alembic** (if not already installed):
```
uv add alembic
```

5. **Generate initial migration** from your SQLAlchemy models:
```
uv run alembic revision --autogenerate -m "initial migration"
```

6. **Apply migration** to create tables in the database:
```
uv run alembic upgrade head
```

7. **Start FastAPI server**:
```
uv run uvicorn main:app --reload
```

8. **Verify API**: open http://127.0.0.1:8000/docs
 in your browser.

This ensures your development environment is fully configured for PostgreSQL and ready for asynchronous operations, while keeping your schema in sync using Alembic migrations.

### Securely Loading the Database URL

For security and portability, you should avoid hardcoding passwords in your code. Instead, store your database URL in an environment variable and load it in database.py:
```
import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:pgAdmin@localhost:5433/blogdb"  # fallback for dev
)

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

```
Set the environment variable in your shell before running the server:
```
# Windows PowerShell
$env:DATABASE_URL="postgresql+asyncpg://postgres:yourpassword@localhost:5433/blogdb"
```

This keeps your credentials out of the source code and ensures other developers can use their own database configuration securely.

## Running Unit Tests
In a VS Code terminal, type the following command to activate the virtual environment,
```
.\.venv\Scripts\Activate.ps1
```
To run the user and posts unit tests,
```
python -m pytest
```
To get a report on code coverage when testing
```
python -m pytest --cov=.
```
## Hosting the blogging web application on the Amazon Web Service cloud platform
This application is containerised using Docker and deployed to AWS using Amazon Elastic Container Service (ECS) 
with images stored in Amazon Elastic Container Registry (ECR). An Application Load Balancer (ALB) is used to 
route external HTTPS traffic to the running container. 

The FastAPI application running inside the ECS Fargate container connects directly to Amazon RDS using a PostgreSQL connection string. ECS itself is not involved in database communication; it is only responsible for running and managing the container.

The FastAPI application running inside the ECS Fargate container uploads and retrieves profile images directly to and from Amazon S3 using the AWS SDK and IAM permissions.

### Architecture Overview
 - FastAPI application runs inside a Docker container
 - Docker image is built locally and pushed to Amazon ECR
 - ECS (Fargate) runs the container in a managed service
 - Application Load Balancer (ALB) exposes the service publicly over HTTPS
 - AWS Certificate Manager (ACM) provides SSL/TLS termination at the load balancer
 - FastAPI app (inside the container) communicates with the database in RDS
 - FastAPI app (inside the container) retrieves and stores profile images in an S3 bucket

### What each AWS piece actually does

| Component                                   | What it is     | What it does                                   |
| ------------------------------------------- | -------------- | ---------------------------------------------- |
| **Amazon Elastic Container Registry (ECR)** | Image storage  | Holds your Docker image layers                 |
| **Amazon Elastic Container Service (ECS)**  | Orchestrator   | Decides *how* and *where* to run containers    |
| **AWS Fargate**                             | Compute engine | Actually provides CPU/RAM to run the container |
| **Amazon RDS**                              | Database       | Stores blog titles and content                 |
| **Amazon S3**                               | Object storage | Stores profile images                          |

### Build & Push Workflow
Ensure Docker Desktop is installed on your local machine.

1. Build Docker image locally.  Open Docker Desktop, navigate to the folder containing the Docker file and open a command prompt:
```
docker build -t fastapi-app .
```
2. Authenticate Docker to AWS ECR:
```
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
```
3. Tag image for ECR:
```
docker tag fastapi-app:latest <ecr-repo-url>:latest
```
4. Push image to ECR:
```
docker push <ecr-repo-url>:latest
```

### Deployment on ECS
1. A new **ECS task definition revision** is created referencing the latest Docker image in ECR
2. The ECS service is updated to use the new task definition
3. ECS pulls the image from ECR and starts a new container
4. **Force new deployment** ensures running tasks are replaced with the updated version
   
### Networking & HTTPS
- The Application Load Balancer handles HTTPS termination using an AWS Certificate Manager (ACM) certificate
- Traffic from ALB to ECS runs over HTTP within the private AWS network
- Proper forwarding headers (X-Forwarded-Proto) ensure the application correctly generates HTTPS URLs

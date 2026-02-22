# A FastAPI Blogging Web Application
This web application is built with the Python **FastApi Framework** and it allows users to enter, update & delete blog posts.

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






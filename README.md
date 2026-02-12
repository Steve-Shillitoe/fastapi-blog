# A FastAPI Blogging Web Application
This web application is built with the Python **FastApi Framework** and it allows users to enter, update & delete blog posts.

**Jinja2 templates** are used to create an HTML frontend for the backend API JSON endpoints. 
**Template inheritance** with a layout file is utilised to simplify the template files. 
Additionally, **Bootstrap** is used for styling. Consequently, the application is configured to use static files for CSS and images.

**Pydantic schemas** are used to validate API requests and responses in FastAPI. **Pydantic schemas** define the API contract - what data goes in and what comes out - and **FastAPI** uses them for validation, serialization, and automatic documentation. Consequently this project contains a schemas file with request and response models, 
that have field validations for minimum and maximum length for strings. 

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



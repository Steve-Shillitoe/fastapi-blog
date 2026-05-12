# BUILD STAGE
FROM python:3.12-slim-bookworm AS builder
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.11.6 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

COPY . .
RUN uv sync --locked --no-dev

# PRODUCTION STAGE
FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y libpq5 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app /app

RUN useradd -m appuser
USER appuser

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]  development

# Start the FastAPI application using Uvicorn when the container launches.
# "main:app" tells Uvicorn to import the object named `app` from main.py.
# "--host 0.0.0.0" binds the server to all network interfaces so it is reachable
# from outside the container (required for Docker / ECS / Kubernetes networking).
# "--port 8000" exposes the app on port 8000 inside the container.
# The JSON array (exec form) ensures the process receives OS signals directly,
# allowing graceful shutdowns and proper handling in container environments.
#  "--proxy-headers", "--forwarded-allow-ips", "*"  ensure correct URL generation behind ALB
CMD ["uvicorn", "main:app",   "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]

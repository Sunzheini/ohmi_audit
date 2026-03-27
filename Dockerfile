# Dockerfile is a script that contains a series of instructions to build a Docker image.

# FROM is used to specify the base image for the Docker image.
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
# Prevents Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Ensures that Python output is sent straight to terminal (e.g. for logging)
ENV PYTHONUNBUFFERED 1
# Tell Poetry not to create a virtualenv — we're already inside a container
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_NO_INTERACTION=1

# Creates and sets /app as the working directory (like cd /app)
# All subsequent commands will run from this directory
WORKDIR /app

# Install system dependencies (including curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy only dependency files first — better Docker layer caching
# (dependencies are re-installed only when pyproject.toml/poetry.lock change)
COPY pyproject.toml poetry.lock ./

# Install production dependencies (skip installing the project root itself)
RUN poetry install --no-root --no-ansi

# Copy the rest of the project
COPY . .

# Copy and make entrypoint executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# collectstatic and migrate are handled in entrypoint.sh at runtime
# (SECRET_KEY and DB are not available during build)

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "ohmi_audit.wsgi:application"]

# Dockerfile is a script that contains a series of instructions to build a Docker image.

# FROM is used to specify the base image for the Docker image.
# Use an official Python runtime as a parent image
FROM python:3.11-slim
#FROM python:3.11-bullseye  # More complete OS base

# Set environment variables
# Prevents Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Ensures that Python output is sent straight to terminal (e.g. for logging)
ENV PYTHONUNBUFFERED 1

# Creates and sets /app as the working directory (like cd /app)
# All subsequent commands will run from this directory
WORKDIR /app

# Install system dependencies
# Updates package lists (apt-get update)
# Installs essential build tools and PostgreSQL client library
# Cleans up to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Celery
RUN pip install celery

# command to optimize build caching
COPY --chown=1000:1000 . .
# Copies all files from your local directory to the container's /app directory
COPY . .

# Collect static files (for production)
# Gathers all static files in one location (for production serving)
RUN python manage.py collectstatic --noinput

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# to run docker on render.com
# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ohmi_audit.wsgi:application"]
# syntax=docker/dockerfile:1
FROM python:3.11-alpine

# Install build dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev

# Set work directory
WORKDIR /app

# Install pip if not present (Alpine sometimes needs this)
RUN python -m ensurepip

# Install uv (fast Python package installer)
RUN pip install --upgrade pip && pip install uv

# Copy dependency files first for layer caching
COPY pyproject.toml ./

# Install dependencies using uv
RUN uv pip install --system .

# Copy application code
COPY . ./app

# Expose port
EXPOSE 8000

# Run the application using uvloop
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop", "--app-dir", "app"]
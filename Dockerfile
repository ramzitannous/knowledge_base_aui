# syntax=docker/dockerfile:1
FROM python:3.13-slim

# Install build and OCR dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        build-essential \
        libffi-dev \
        tesseract-ocr \
        tesseract-ocr-eng \
        libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Create workspace directory
RUN mkdir /workspace /workspace/app

# Set work directory
WORKDIR /workspace

# Install pip if not present (Alpine sometimes needs this)
RUN python -m ensurepip

# Install uv (fast Python package installer)
RUN pip install --upgrade pip && pip install uv

# Copy dependency files first for layer caching
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies using uv
RUN uv pip install --system .

# Copy application code
COPY ./app ./app

# Expose port
EXPOSE 8000

# Run the application using uvloop
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop"]
# ============================================================================
# Backend API Dockerfile
# ============================================================================
# Builds the FastAPI backend application container.
# Uses the official FastAPI base image with uvicorn and gunicorn.
# ============================================================================

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Copy requirements file and install Python dependencies
COPY ./requirements.txt /app/requirements.txt

# Install all Python packages from requirements.txt
# --no-cache-dir: Reduces image size by not storing pip cache
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy application code into container
COPY ./app /app/app
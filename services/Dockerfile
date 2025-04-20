FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY ./services ./services
COPY ./files ./files

# Set env vars (can be overridden in docker-compose.yml)
ENV PYTHONPATH=.

# Default: start FastAPI
CMD ["uvicorn", "services.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy demo UI
COPY ./demo ./demo

# Run Gradio app
CMD ["python", "demo/demo.py"]

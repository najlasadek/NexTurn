# Business Service Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY business-service/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities
COPY shared/ /app/shared/

# Copy application code
COPY business-service/ .

# Set Python path to include shared and app directory
ENV PYTHONPATH=/app:/app/shared

# Expose port
EXPOSE 5002

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV BUSINESS_SERVICE_PORT=5002
ENV QUEUE_SERVICE_URL=http://queue-service:5003

# Run the application
CMD ["python", "app/app.py"]

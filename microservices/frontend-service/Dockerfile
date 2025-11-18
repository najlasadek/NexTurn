# Frontend Gateway Service Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY microservices/frontend-service/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY microservices/frontend-service/ .

# Copy templates and static files from parent directory
COPY templates/ /app/templates/
COPY static/ /app/static/

# Expose port
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FRONTEND_SERVICE_PORT=5000

# Run the application
CMD ["python", "app/app.py"]

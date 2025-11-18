FROM python:3.11-slim

WORKDIR /app

# Copy ONLY this service's requirements from the correct folder
COPY feedback-service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities
COPY shared/ /app/shared/

# Copy this service's code into /app
COPY feedback-service/ ./

EXPOSE 5005

CMD ["python", "app/app.py"]

FROM python:3.9-slim

WORKDIR /app

COPY ticket-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ticket-service/ /app

ENV PYTHONPATH=/app

EXPOSE 5004

CMD ["python", "app/app.py"]

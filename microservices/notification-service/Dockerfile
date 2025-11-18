FROM python:3.9-slim

WORKDIR /app

COPY notification-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY notification-service/ /app

ENV PYTHONPATH=/app

EXPOSE 5007

CMD ["python", "app/app.py"]

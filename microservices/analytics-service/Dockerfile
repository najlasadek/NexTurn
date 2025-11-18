FROM python:3.9-slim

WORKDIR /app

COPY analytics-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY analytics-service/ /app

ENV PYTHONPATH=/app

EXPOSE 5006

CMD ["python", "app/app.py"]

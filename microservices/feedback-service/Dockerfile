FROM python:3.9-slim

WORKDIR /app

COPY feedback-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY feedback-service/ /app

ENV PYTHONPATH=/app

EXPOSE 5005

CMD ["python", "app/app.py"]

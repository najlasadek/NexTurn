"""
Frontend Service Configuration
"""
import os

class Config:
    # Service Configuration
    FRONTEND_SERVICE_PORT = int(os.getenv('FRONTEND_SERVICE_PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

    # Microservices URLs
    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth-service:5001')
    BUSINESS_SERVICE_URL = os.getenv('BUSINESS_SERVICE_URL', 'http://business-service:5002')
    QUEUE_SERVICE_URL = os.getenv('QUEUE_SERVICE_URL', 'http://queue-service:5003')
    FEEDBACK_SERVICE_URL = os.getenv('FEEDBACK_SERVICE_URL', 'http://feedback-service:5005')

    # Session Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

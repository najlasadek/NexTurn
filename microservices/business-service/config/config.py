"""
Configuration for business service
"""
import os


class Config:
    """Base configuration"""
    DB_PATH = os.getenv('DB_PATH', '../db/business.db')
    QUEUE_SERVICE_URL = os.getenv('QUEUE_SERVICE_URL', 'http://localhost:5003')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

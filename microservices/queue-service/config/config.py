"""
Configuration for queue service
"""
import os


class Config:
    """Base configuration"""
    DB_PATH = os.getenv('DB_PATH', '../db/queue.db')


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

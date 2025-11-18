"""
Authentication Service - Main Application
"""
from flask import Flask
from flask_cors import CORS
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from models import User
from routes import init_routes
from db.init_db import init_database

# Configuration
DB_PATH = os.path.join(os.path.dirname(__file__), '../db/auth.db')
PORT = int(os.getenv('AUTH_SERVICE_PORT', 5001))

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize database
init_database(DB_PATH)

# Initialize user model
user_model = User(DB_PATH)

# Register routes
auth_routes = init_routes(user_model)
app.register_blueprint(auth_routes, url_prefix='/auth')


@app.route('/')
def index():
    """Root endpoint"""
    return {
        'service': 'Authentication Service',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/auth/health',
            'signup': '/auth/signup',
            'login': '/auth/login',
            'verify': '/auth/verify',
            'profile': '/auth/profile'
        }
    }


if __name__ == '__main__':
    print(f"🔐 Authentication Service starting on port {PORT}...")
    app.run(host='0.0.0.0', port=PORT, debug=True)

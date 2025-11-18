"""
Business Service - Main Application
"""
from flask import Flask
from flask_cors import CORS
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from models import Business
from routes import init_routes
from db.init_db import init_database

# Configuration
DB_PATH = os.path.join(os.path.dirname(__file__), '../db/business.db')
PORT = int(os.getenv('BUSINESS_SERVICE_PORT', 5002))
QUEUE_SERVICE_URL = os.getenv('QUEUE_SERVICE_URL', 'http://localhost:5003')

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize database
init_database(DB_PATH)

# Initialize business model
business_model = Business(DB_PATH, QUEUE_SERVICE_URL)

# Register routes
business_routes = init_routes(business_model)
app.register_blueprint(business_routes, url_prefix='/api')


@app.route('/')
def index():
    """Root endpoint"""
    return {
        'service': 'Business Service',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'create_business': '/api/businesses [POST]',
            'get_all_businesses': '/api/businesses [GET]',
            'get_business': '/api/businesses/<id> [GET]',
            'my_businesses': '/api/businesses/my-businesses [GET]',
            'update_business': '/api/businesses/<id> [PUT]',
            'delete_business': '/api/businesses/<id> [DELETE]',
            'business_stats': '/api/businesses/<id>/stats [GET]'
        }
    }


if __name__ == '__main__':
    print(f"🏢 Business Service starting on port {PORT}...")
    app.run(host='0.0.0.0', port=PORT, debug=True)

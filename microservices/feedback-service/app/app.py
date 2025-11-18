"""
Feedback Service - Main Application
"""
from flask import Flask
from flask_cors import CORS
import os
import sys

# Add parent directory to path for imports (same trick as business-service)
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from models import Feedback
from routes import init_routes
from db.init_db import init_database

# Configuration
DB_PATH = os.path.join(os.path.dirname(__file__), '../db/feedback.db')
PORT = int(os.getenv('FEEDBACK_SERVICE_PORT', 5005))

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize database
init_database(DB_PATH)

# Initialize Feedback model
feedback_model = Feedback(DB_PATH)

# Register routes
feedback_routes = init_routes(feedback_model)
app.register_blueprint(feedback_routes, url_prefix='/')

@app.route('/')
def index():
    """Root endpoint"""
    return {
        'service': 'Feedback Service',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'submit_feedback': '/feedback [POST]',
            'list_feedback_for_business': '/feedback/business/<id> [GET]',
            'get_feedback': '/feedback/<id> [GET]',
            'average_rating': '/feedback/business/<id>/average [GET]',
        }
    }

if __name__ == '__main__':
    print(f"⭐ Feedback Service starting on port {PORT}...")
    app.run(host='0.0.0.0', port=PORT, debug=True)

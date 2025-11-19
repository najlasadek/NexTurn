from flask import Flask
from flask_cors import CORS
import os
import sys

# Allow imports from parent folder (for db/models/routes)
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from models import Feedback
from routes import init_routes
from db.init_db import init_database

# Database path inside container
DB_PATH = os.getenv('DB_PATH', os.path.join(os.path.dirname(__file__), '../db/feedback.db'))
PORT = int(os.getenv('FEEDBACK_SERVICE_PORT', 5005))  # default: 5005

app = Flask(__name__)
CORS(app)

# Create database & table
init_database(DB_PATH)

# Create model instance
feedback_model = Feedback(DB_PATH)

# Register API routes
feedback_routes = init_routes(feedback_model)
app.register_blueprint(feedback_routes, url_prefix='/')

@app.route('/')
def index():
    return {
        'service': 'Feedback Service',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'add_feedback': '/feedback [POST]',
            'get_feedback': '/feedback/<id> [GET]',
            'list_business_feedback': '/feedback/business/<id> [GET]',
            'average_rating': '/feedback/business/<id>/average [GET]'
        }
    }

if __name__ == '__main__':
    print(f"🚀 Feedback Service running on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=True)

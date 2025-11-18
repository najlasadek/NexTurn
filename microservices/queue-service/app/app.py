"""
Queue Service - Main Application
"""
from flask import Flask
from flask_cors import CORS
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from models import QueueModel, TicketModel
from routes import init_routes
from db.init_db import init_database

# Configuration
DB_PATH = os.path.join(os.path.dirname(__file__), '../db/queue.db')
PORT = int(os.getenv('QUEUE_SERVICE_PORT', 5003))

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize database
init_database(DB_PATH)

# Initialize models
queue_model = QueueModel(DB_PATH)
ticket_model = TicketModel(DB_PATH)

# Register routes
queue_routes = init_routes(queue_model, ticket_model)
app.register_blueprint(queue_routes, url_prefix='/api')


@app.route('/')
def index():
    """Root endpoint"""
    return {
        'service': 'Queue Management Service',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'create_queue': '/api/queues [POST]',
            'get_queue': '/api/queues/<id> [GET]',
            'business_queues': '/api/queues/business/<business_id> [GET]',
            'update_queue': '/api/queues/<id> [PUT]',
            'delete_queue': '/api/queues/<id> [DELETE]',
            'join_queue': '/api/queues/<id>/join [POST]',
            'get_ticket': '/api/tickets/<ticket_id> [GET]',
            'cancel_ticket': '/api/tickets/<ticket_id>/cancel [POST]',
            'serve_next': '/api/queues/<id>/serve-next [POST]',
            'my_history': '/api/tickets/my-history [GET]',
            'my_active_ticket': '/api/tickets/my-active [GET]'
        }
    }


if __name__ == '__main__':
    print(f"📋 Queue Management Service starting on port {PORT}...")
    app.run(host='0.0.0.0', port=PORT, debug=True)

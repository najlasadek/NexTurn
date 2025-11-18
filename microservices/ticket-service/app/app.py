from flask import Flask
from flask_cors import CORS
import os
import sys

# Allow imports from parent folder
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from models import TicketHistory
from routes import init_routes
from db.init_db import init_database

DB_PATH = os.path.join(os.path.dirname(__file__), '../db/ticket.db')
PORT = int(os.getenv('TICKET_SERVICE_PORT', 5004))

app = Flask(__name__)
CORS(app)

# Init DB and table
init_database(DB_PATH)

# Model instance
ticket_model = TicketHistory(DB_PATH)

# Routes
ticket_bp = init_routes(ticket_model)
app.register_blueprint(ticket_bp, url_prefix='/')

@app.route('/')
def index():
    return {
        'service': 'Ticket Service',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'get_ticket': '/tickets/<ticketId> [GET]',
            'update_alerts': '/tickets/<ticketId>/alerts [PUT]',
            'user_tickets': '/tickets/user/<userId> [GET]',
        }
    }

if __name__ == '__main__':
    print(f"🎫 Ticket Service running on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=True)

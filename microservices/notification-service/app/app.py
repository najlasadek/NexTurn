from flask import Flask
from flask_cors import CORS
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from models import NotificationStore
from routes import init_routes
from db.init_db import init_database

DB_PATH = os.getenv('DB_PATH', os.path.join(os.path.dirname(__file__), '../db/notifications.db'))
PORT = int(os.getenv('NOTIFICATION_SERVICE_PORT', 5007))

app = Flask(__name__)
CORS(app)

init_database(DB_PATH)

notif_model = NotificationStore(DB_PATH)
notif_bp = init_routes(notif_model)
app.register_blueprint(notif_bp, url_prefix='/')

@app.route('/')
def index():
    return {'service': 'Notification Service', 'status': 'running'}

if __name__ == '__main__':
    print(f"🔔 Notification Service running on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=True)

from flask import Flask
from flask_cors import CORS
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from models import Analytics
from routes import init_routes
from db.init_db import init_database

DB_PATH = os.path.join(os.path.dirname(__file__), '../db/analytics.db')
PORT = int(os.getenv('ANALYTICS_SERVICE_PORT', 5006))

app = Flask(__name__)
CORS(app)

init_database(DB_PATH)

analytics_model = Analytics(DB_PATH)
analytics_bp = init_routes(analytics_model)
app.register_blueprint(analytics_bp, url_prefix='/')

@app.route('/')
def index():
    return {
        'service': 'Analytics Service',
        'status': 'running'
    }

if __name__ == '__main__':
    print(f"📊 Analytics Service running on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=True)

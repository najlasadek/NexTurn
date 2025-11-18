from flask import Flask
from flask_cors import CORS
from config.config import Config
from db.init_db import init_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    # Register routes
    from app.routes import feedback_bp
    app.register_blueprint(feedback_bp, url_prefix="/feedback")

    # Initialize DB
    with app.app_context():
        init_db()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)

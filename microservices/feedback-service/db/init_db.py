from shared.database import db

def init_db():
    db.create_all()

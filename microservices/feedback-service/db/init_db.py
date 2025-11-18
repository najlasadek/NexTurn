from shared.database import db

def init_db():
    db.create_all()

import os
import sqlite3

def init_database(db_path: str):
    """
    Create the feedback.db file and feedback table if they do not exist.
    """
    # Ensure db directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            business_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    conn.commit()
    conn.close()
    print(f"[feedback-service] Database initialized at {db_path}")

import os
import sqlite3

DB_FILENAME = "notifications.db"


def _default_db_path():
    base_dir = os.path.dirname(__file__)
    return os.path.join(base_dir, DB_FILENAME)


def init_database(db_path=None):
    if db_path is None:
        db_path = _default_db_path()

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            channel TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL,
            scheduled_for TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    conn.commit()
    conn.close()
    print(f"[notification-service] DB initialized at {db_path}")
    return db_path


def init_db(db_path=None):
    init_database(db_path)

"""
Initialize authentication service database
"""
import sqlite3
import os


def init_database(db_path):
    """Initialize the users database"""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            organization TEXT,
            user_type TEXT DEFAULT 'customer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print(f"Authentication database initialized at {db_path}")


if __name__ == '__main__':
    DB_PATH = os.path.join(os.path.dirname(__file__), 'auth.db')
    init_database(DB_PATH)

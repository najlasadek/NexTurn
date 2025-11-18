"""
Initialize business service database
"""
import sqlite3
import os


def init_database(db_path):
    """Initialize the businesses database"""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create businesses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS businesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            address TEXT,
            owner_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create index on owner_id for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_owner_id ON businesses(owner_id)
    """)

    conn.commit()
    conn.close()
    print(f"Business database initialized at {db_path}")


if __name__ == '__main__':
    DB_PATH = os.path.join(os.path.dirname(__file__), 'business.db')
    init_database(DB_PATH)

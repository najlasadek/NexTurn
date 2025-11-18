"""
Initialize queue service database
"""
import sqlite3
import os


def init_database(db_path):
    """Initialize the queues database"""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create queues table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            avg_service_time INTEGER DEFAULT 5,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create queue_history table (tickets)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queue_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            queue_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            ticket_id TEXT NOT NULL UNIQUE,
            position INTEGER,
            join_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            leave_time TIMESTAMP,
            wait_time INTEGER,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (queue_id) REFERENCES queues(id)
        )
    """)

    # Create indexes for better performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_business_id ON queues(business_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_queue_id ON queue_history(queue_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_id ON queue_history(user_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ticket_id ON queue_history(ticket_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_status ON queue_history(status)
    """)

    conn.commit()
    conn.close()
    print(f"Queue database initialized at {db_path}")


if __name__ == '__main__':
    DB_PATH = os.path.join(os.path.dirname(__file__), 'queue.db')
    init_database(DB_PATH)

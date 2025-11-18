import os
import sqlite3

# Database file name inside /app/db in the container
DB_FILENAME = "feedback.db"


def _get_default_db_path() -> str:
    """
    Returns the default DB path, based on this file's directory.
    Inside the container this will be /app/db/feedback.db
    """
    base_dir = os.path.dirname(__file__)  # /app/db
    return os.path.join(base_dir, DB_FILENAME)


def init_database(db_path: str | None = None) -> str:
    """
    Create the feedback.db file and feedback table if they do not exist.
    If db_path is None, use the default /app/db/feedback.db.
    Returns the actual db_path used.
    """
    if db_path is None:
        db_path = _get_default_db_path()

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
    return db_path


def init_db(*args, **kwargs) -> None:
    """
    Backwards-compatible alias for init_database.

    - If called as init_db() -> uses default path.
    - If called as init_db('/some/path') -> uses that path.
    """
    if args:
        db_path = args[0]
    else:
        db_path = kwargs.get("db_path", None)
    init_database(db_path)

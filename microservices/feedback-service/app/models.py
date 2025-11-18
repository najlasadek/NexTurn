import sqlite3

class Feedback:
    """
    Feedback model: wraps all DB operations for feedback-service.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_feedback(self, user_id: int, business_id: int, rating: int, comment: str = ""):
        conn = self._get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO feedback (user_id, business_id, rating, comment)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, business_id, rating, comment),
        )
        conn.commit()
        new_id = cur.lastrowid

        cur.execute("SELECT * FROM feedback WHERE id = ?", (new_id,))
        row = cur.fetchone()
        conn.close()

        return dict(row) if row else None

    def get_feedback_by_id(self, feedback_id: int):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM feedback WHERE id = ?", (feedback_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_feedback_for_business(self, business_id: int):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM feedback
            WHERE business_id = ?
            ORDER BY created_at DESC
            """,
            (business_id,),
        )
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_average_rating_for_business(self, business_id: int):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT AVG(rating) AS avg_rating, COUNT(*) AS count
            FROM feedback
            WHERE business_id = ?
            """,
            (business_id,),
        )
        row = cur.fetchone()
        conn.close()

        avg = row["avg_rating"] if row and row["avg_rating"] is not None else None
        count = row["count"] if row else 0

        return {
            "business_id": business_id,
            "average_rating": float(avg) if avg is not None else None,
            "count": int(count),
        }

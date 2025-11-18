import sqlite3
import uuid


class TicketHistory:
    """
    Stores ticket history in a local ticket.db (queue_history table).
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_ticket(self, queue_id: int, user_id: int, status: str = "active"):
        conn = self._get_connection()
        cur = conn.cursor()

        ticket_id = str(uuid.uuid4())

        cur.execute(
            """
            INSERT INTO queue_history (ticket_id, queue_id, user_id, status)
            VALUES (?, ?, ?, ?)
            """,
            (ticket_id, queue_id, user_id, status),
        )
        conn.commit()

        cur.execute("SELECT * FROM queue_history WHERE ticket_id = ?", (ticket_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_ticket_by_ticket_id(self, ticket_id: str):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM queue_history WHERE ticket_id = ?",
            (ticket_id,),
        )
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_tickets_for_user(self, user_id: int):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM queue_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        )
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_alerts(self, ticket_id: str, email: bool, sms: bool, push: bool):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE queue_history
            SET alert_email = ?, alert_sms = ?, alert_push = ?
            WHERE ticket_id = ?
            """,
            (int(email), int(sms), int(push), ticket_id),
        )
        conn.commit()
        cur.execute("SELECT * FROM queue_history WHERE ticket_id = ?", (ticket_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_status(self, ticket_id: str, status: str):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE queue_history
            SET status = ?
            WHERE ticket_id = ?
            """,
            (status, ticket_id),
        )
        conn.commit()
        cur.execute("SELECT * FROM queue_history WHERE ticket_id = ?", (ticket_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

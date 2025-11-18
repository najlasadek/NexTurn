import sqlite3
from datetime import datetime


class NotificationStore:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def send_notification(self, user_id: int, channel: str, message: str):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO notifications (user_id, channel, message, status)
            VALUES (?, ?, ?, 'sent')
            """,
            (user_id, channel, message),
        )
        conn.commit()
        new_id = cur.lastrowid
        cur.execute("SELECT * FROM notifications WHERE id = ?", (new_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def schedule_notification(self, user_id: int, channel: str, message: str, scheduled_for: str):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO notifications (user_id, channel, message, status, scheduled_for)
            VALUES (?, ?, ?, 'scheduled', ?)
            """,
            (user_id, channel, message, scheduled_for),
        )
        conn.commit()
        new_id = cur.lastrowid
        cur.execute("SELECT * FROM notifications WHERE id = ?", (new_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_notifications_for_user(self, user_id: int):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM notifications
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        )
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

import sqlite3


class Analytics:
    """
    Simple analytics service over a local queue_history table.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_queue_analytics(self, queue_id: int):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                COUNT(*) AS tickets,
                AVG(wait_time_seconds) AS avg_wait,
                MIN(wait_time_seconds) AS min_wait,
                MAX(wait_time_seconds) AS max_wait
            FROM queue_history
            WHERE queue_id = ?
            """,
            (queue_id,),
        )
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else {}

    def get_business_analytics(self, business_id: int):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                COUNT(*) AS tickets,
                AVG(wait_time_seconds) AS avg_wait,
                MIN(wait_time_seconds) AS min_wait,
                MAX(wait_time_seconds) AS max_wait
            FROM queue_history
            WHERE business_id = ?
            """,
            (business_id,),
        )
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else {}

    def get_wait_time_stats(self):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                COUNT(*) AS tickets,
                AVG(wait_time_seconds) AS avg_wait,
                MIN(wait_time_seconds) AS min_wait,
                MAX(wait_time_seconds) AS max_wait
            FROM queue_history
            """
        )
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else {}

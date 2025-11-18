"""
Queue and Ticket models for queue service
"""
import sys
import os
import uuid
from datetime import datetime

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))
from database import Database


class QueueModel:
    """Queue model"""

    def __init__(self, db_path):
        self.db = Database(db_path)

    def create_queue(self, business_id, name, avg_service_time=5):
        """Create a new queue"""
        query = """
            INSERT INTO queues (business_id, name, avg_service_time, is_active)
            VALUES (?, ?, ?, 1)
        """
        try:
            queue_id = self.db.execute_insert(query, (business_id, name, avg_service_time))
            return queue_id, None
        except Exception as e:
            return None, str(e)

    def get_queue_by_id(self, queue_id):
        """Get queue by ID"""
        query = "SELECT * FROM queues WHERE id = ?"
        results = self.db.execute_query(query, (queue_id,))
        if results:
            return dict(results[0])
        return None

    def get_queues_by_business(self, business_id):
        """Get all queues for a business"""
        query = """
            SELECT id, business_id, name, avg_service_time, is_active, created_at
            FROM queues
            WHERE business_id = ? AND is_active = 1
            ORDER BY created_at
        """
        results = self.db.execute_query(query, (business_id,))
        return [dict(row) for row in results]

    def update_queue(self, queue_id, **kwargs):
        """Update queue information"""
        allowed_fields = ['name', 'avg_service_time', 'is_active']
        updates = []
        values = []

        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                updates.append(f"{key} = ?")
                values.append(value)

        if not updates:
            return False

        values.append(queue_id)
        query = f"UPDATE queues SET {', '.join(updates)} WHERE id = ?"

        try:
            self.db.execute_update(query, tuple(values))
            return True
        except Exception:
            return False

    def delete_queue(self, queue_id):
        """Soft delete a queue"""
        query = "UPDATE queues SET is_active = 0 WHERE id = ?"
        try:
            self.db.execute_update(query, (queue_id,))
            return True
        except Exception:
            return False

    def get_queue_size(self, queue_id):
        """Get current size of queue"""
        query = """
            SELECT COUNT(*) as size
            FROM queue_history
            WHERE queue_id = ? AND status = 'active'
        """
        results = self.db.execute_query(query, (queue_id,))
        if results:
            return results[0]['size']
        return 0

    def get_active_tickets(self, queue_id):
        """Get all active tickets in queue"""
        query = """
            SELECT id, queue_id, user_id, ticket_id, position, join_time, status
            FROM queue_history
            WHERE queue_id = ? AND status = 'active'
            ORDER BY position
        """
        results = self.db.execute_query(query, (queue_id,))
        return [dict(row) for row in results]


class TicketModel:
    """Ticket model"""

    def __init__(self, db_path):
        self.db = Database(db_path)

    def create_ticket(self, queue_id, user_id):
        """Create a new ticket and add user to queue"""
        # Get current queue size to determine position
        query = """
            SELECT COALESCE(MAX(position), 0) + 1 as next_position
            FROM queue_history
            WHERE queue_id = ? AND status = 'active'
        """
        results = self.db.execute_query(query, (queue_id,))
        position = results[0]['next_position'] if results else 1

        # Generate unique ticket ID
        ticket_id = str(uuid.uuid4())

        # Insert ticket
        insert_query = """
            INSERT INTO queue_history (queue_id, user_id, ticket_id, position, status)
            VALUES (?, ?, ?, ?, 'active')
        """
        try:
            self.db.execute_insert(insert_query, (queue_id, user_id, ticket_id, position))
            return ticket_id, position, None
        except Exception as e:
            return None, None, str(e)

    def get_ticket_by_id(self, ticket_id):
        """Get ticket by ticket ID"""
        query = """
            SELECT id, queue_id, user_id, ticket_id, position, join_time,
                   leave_time, wait_time, status
            FROM queue_history
            WHERE ticket_id = ?
        """
        results = self.db.execute_query(query, (ticket_id,))
        if results:
            return dict(results[0])
        return None

    def get_user_active_ticket(self, user_id):
        """Get user's active ticket if any"""
        query = """
            SELECT id, queue_id, user_id, ticket_id, position, join_time, status
            FROM queue_history
            WHERE user_id = ? AND status = 'active'
            LIMIT 1
        """
        results = self.db.execute_query(query, (user_id,))
        if results:
            return dict(results[0])
        return None

    def cancel_ticket(self, ticket_id, user_id):
        """Cancel a ticket"""
        # Get ticket first
        ticket = self.get_ticket_by_id(ticket_id)
        if not ticket:
            return False, 'Ticket not found'

        # Verify ownership
        if ticket['user_id'] != user_id:
            return False, 'Unauthorized'

        # Don't allow canceling if user is first in queue
        if ticket['position'] == 1:
            return False, 'Cannot cancel when you are next in line'

        # Update ticket status
        query = """
            UPDATE queue_history
            SET leave_time = CURRENT_TIMESTAMP,
                status = 'cancelled',
                wait_time = (strftime('%s', 'now') - strftime('%s', join_time)) / 60
            WHERE ticket_id = ? AND status = 'active'
        """
        try:
            self.db.execute_update(query, (ticket_id,))

            # Recalculate positions
            self._recalculate_positions(ticket['queue_id'], ticket['position'])

            return True, None
        except Exception as e:
            return False, str(e)

    def serve_next_customer(self, queue_id):
        """Serve the next customer in queue"""
        # Get first ticket
        query = """
            SELECT id, ticket_id, user_id, position
            FROM queue_history
            WHERE queue_id = ? AND status = 'active'
            ORDER BY position
            LIMIT 1
        """
        results = self.db.execute_query(query, (queue_id,))

        if not results:
            return None, 'No customers in queue'

        ticket = dict(results[0])

        # Mark as completed
        update_query = """
            UPDATE queue_history
            SET leave_time = CURRENT_TIMESTAMP,
                status = 'completed',
                wait_time = (strftime('%s', 'now') - strftime('%s', join_time)) / 60
            WHERE id = ?
        """
        try:
            self.db.execute_update(update_query, (ticket['id'],))

            # Recalculate positions
            self._recalculate_positions(queue_id, ticket['position'])

            return ticket, None
        except Exception as e:
            return None, str(e)

    def _recalculate_positions(self, queue_id, removed_position):
        """Recalculate positions after removing a ticket"""
        query = """
            UPDATE queue_history
            SET position = position - 1
            WHERE queue_id = ? AND status = 'active' AND position > ?
        """
        try:
            self.db.execute_update(query, (queue_id, removed_position))
        except Exception as e:
            print(f"Error recalculating positions: {e}")

    def get_user_history(self, user_id, limit=50):
        """Get user's queue history"""
        query = """
            SELECT id, queue_id, user_id, ticket_id, position, join_time,
                   leave_time, wait_time, status
            FROM queue_history
            WHERE user_id = ?
            ORDER BY join_time DESC
            LIMIT ?
        """
        results = self.db.execute_query(query, (user_id, limit))
        return [dict(row) for row in results]

    def calculate_eta(self, queue_id, position):
        """Calculate estimated wait time"""
        # Get queue's average service time
        query = "SELECT avg_service_time FROM queues WHERE id = ?"
        results = self.db.execute_query(query, (queue_id,))

        if not results:
            return 0

        avg_service_time = results[0]['avg_service_time']
        # ETA = (position - 1) * avg_service_time
        return max(0, (position - 1) * avg_service_time)

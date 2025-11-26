"""
Business model for business service
"""
import sys
import os
import requests

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))
from database import Database


class Business:
    """Business model"""

    def __init__(self, db_path, queue_service_url=None):
        self.db = Database(db_path)
        self.queue_service_url = queue_service_url or os.getenv('QUEUE_SERVICE_URL', 'http://localhost:5003')

    def create_business(self, name, description, category, address, owner_id):
        """Create a new business"""
        query = """
            INSERT INTO businesses (name, description, category, address, owner_id)
            VALUES (?, ?, ?, ?, ?)
        """
        try:
            business_id = self.db.execute_insert(
                query,
                (name, description, category, address, owner_id)
            )

            # Create default queue for this business via Queue Service
            self._create_default_queue(business_id)

            return business_id, None
        except Exception as e:
            return None, str(e)

    def _create_default_queue(self, business_id):
        """Create a default queue for a new business"""
        try:
            # Call Queue Service to create default queue
            response = requests.post(
                f"{self.queue_service_url}/api/queues",
                json={
                    'business_id': business_id,
                    'name': 'Main Queue',
                    'avg_service_time': 5
                },
                timeout=5
            )
            return response.status_code == 201
        except Exception as e:
            print(f"Warning: Could not create default queue: {e}")
            return False

    def get_business_by_id(self, business_id):
        """Get business by ID"""
        query = "SELECT * FROM businesses WHERE id = ?"
        results = self.db.execute_query(query, (business_id,))
        if results:
            return dict(results[0])
        return None

    def get_all_businesses(self):
        """Get all businesses"""
        query = """
            SELECT id, name, description, category, address, owner_id, created_at
            FROM businesses
            ORDER BY created_at DESC
        """
        results = self.db.execute_query(query)
        return [dict(row) for row in results]

    def get_businesses_by_owner(self, owner_id):
        """Get businesses owned by a specific user"""
        query = """
            SELECT id, name, description, category, address, owner_id, created_at
            FROM businesses
            WHERE owner_id = ?
            ORDER BY created_at DESC
        """
        results = self.db.execute_query(query, (owner_id,))
        return [dict(row) for row in results]

    def update_business(self, business_id, owner_id, **kwargs):
        """Update business information"""
        # Verify ownership
        business = self.get_business_by_id(business_id)
        if not business or business['owner_id'] != owner_id:
            return False, 'Unauthorized or business not found'

        allowed_fields = ['name', 'description', 'category', 'address']
        updates = []
        values = []

        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                updates.append(f"{key} = ?")
                values.append(value)

        if not updates:
            return False, 'No valid fields to update'

        values.append(business_id)
        query = f"UPDATE businesses SET {', '.join(updates)} WHERE id = ?"

        try:
            self.db.execute_update(query, tuple(values))
            return True, None
        except Exception as e:
            return False, str(e)

    def delete_business(self, business_id, owner_id):
        """Delete a business"""
        # Verify ownership
        business = self.get_business_by_id(business_id)
        if not business or business['owner_id'] != owner_id:
            return False, 'Unauthorized or business not found'

        query = "DELETE FROM businesses WHERE id = ?"
        try:
            self.db.execute_update(query, (business_id,))
            return True, None
        except Exception as e:
            return False, str(e)

    def get_business_stats(self, business_id):
        """Get business statistics (placeholder for future analytics)"""
        business = self.get_business_by_id(business_id)
        if not business:
            return None

        # In the future, this could aggregate data from Queue Service
        return {
            'business_id': business_id,
            'total_queues': 0,  # To be fetched from Queue Service
            'total_customers_served': 0,  # To be fetched from Analytics Service
            'average_rating': 0.0  # To be fetched from Feedback Service
        }

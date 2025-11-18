"""
User model for authentication service
"""
from werkzeug.security import generate_password_hash, check_password_hash
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))
from database import Database


class User:
    """User model"""

    def __init__(self, db_path):
        self.db = Database(db_path)

    def create_user(self, full_name, email, password, organization=None):
        """Create a new user"""
        # Check if user already exists
        existing_user = self.get_user_by_email(email)
        if existing_user:
            return None, 'Email already registered'

        # Hash password
        password_hash = generate_password_hash(password)

        # Insert user
        query = """
            INSERT INTO users (full_name, email, password_hash, organization)
            VALUES (?, ?, ?, ?)
        """
        try:
            user_id = self.db.execute_insert(query, (full_name, email, password_hash, organization))
            return user_id, None
        except Exception as e:
            return None, str(e)

    def get_user_by_email(self, email):
        """Get user by email"""
        query = "SELECT * FROM users WHERE email = ?"
        results = self.db.execute_query(query, (email,))
        if results:
            return dict(results[0])
        return None

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = ?"
        results = self.db.execute_query(query, (user_id,))
        if results:
            user = dict(results[0])
            # Remove password hash from response
            user.pop('password_hash', None)
            return user
        return None

    def verify_password(self, email, password):
        """Verify user password"""
        user = self.get_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            return user
        return None

    def update_user(self, user_id, **kwargs):
        """Update user information"""
        allowed_fields = ['full_name', 'organization']
        updates = []
        values = []

        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)

        if not updates:
            return False

        values.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"

        try:
            self.db.execute_update(query, tuple(values))
            return True
        except Exception:
            return False

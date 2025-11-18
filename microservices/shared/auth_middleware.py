"""
JWT Authentication middleware for microservices
"""
import jwt
import os
from functools import wraps
from flask import request, jsonify


# Secret key for JWT (in production, use environment variable)
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = 'HS256'


def generate_token(user_id, email):
    """Generate JWT token for a user"""
    payload = {
        'user_id': user_id,
        'email': email
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_token(token):
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Decorator to require JWT token for routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'success': False, 'message': 'Invalid token format'}), 401

        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401

        # Decode token
        payload = decode_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Token is invalid or expired'}), 401

        # Add user info to request
        request.user_id = payload['user_id']
        request.user_email = payload['email']

        return f(*args, **kwargs)

    return decorated

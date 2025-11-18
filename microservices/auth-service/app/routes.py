"""
Routes for authentication service
"""
from flask import Blueprint, request
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))
from response import success_response, error_response, validation_error
from auth_middleware import generate_token, token_required

auth_bp = Blueprint('auth', __name__)


def init_routes(user_model):
    """Initialize routes with user model"""

    @auth_bp.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return success_response(data={'status': 'healthy', 'service': 'auth-service'})

    @auth_bp.route('/signup', methods=['POST'])
    def signup():
        """Register a new user"""
        data = request.get_json()

        # Validate input
        required_fields = ['full_name', 'email', 'password', 'confirm_password']
        errors = {}

        for field in required_fields:
            if not data.get(field):
                errors[field] = f'{field} is required'

        if errors:
            return validation_error(errors)

        # Check password match
        if data['password'] != data['confirm_password']:
            return error_response('Passwords do not match', 400)

        # Create user
        user_id, error = user_model.create_user(
            full_name=data['full_name'],
            email=data['email'].lower().strip(),
            password=data['password'],
            organization=data.get('organization', '')
        )

        if error:
            return error_response(error, 400)

        return success_response(
            data={'user_id': user_id},
            message='Account created successfully',
            status_code=201
        )

    @auth_bp.route('/login', methods=['POST'])
    def login():
        """Login user and return JWT token"""
        data = request.get_json()

        # Validate input
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')

        if not email or not password:
            return error_response('Email and password are required', 400)

        # Verify credentials
        user = user_model.verify_password(email, password)
        if not user:
            return error_response('Invalid email or password', 401)

        # Generate JWT token
        token = generate_token(user['id'], user['email'])

        return success_response(
            data={
                'token': token,
                'user': {
                    'id': user['id'],
                    'full_name': user['full_name'],
                    'email': user['email'],
                    'organization': user['organization']
                }
            },
            message='Login successful'
        )

    @auth_bp.route('/verify', methods=['GET'])
    @token_required
    def verify():
        """Verify JWT token and return user info"""
        user = user_model.get_user_by_id(request.user_id)

        if not user:
            return error_response('User not found', 404)

        return success_response(
            data={'user': user},
            message='Token is valid'
        )

    @auth_bp.route('/profile', methods=['GET'])
    @token_required
    def get_profile():
        """Get user profile"""
        user = user_model.get_user_by_id(request.user_id)

        if not user:
            return error_response('User not found', 404)

        return success_response(data={'user': user})

    @auth_bp.route('/profile', methods=['PUT'])
    @token_required
    def update_profile():
        """Update user profile"""
        data = request.get_json()

        # Update user
        success = user_model.update_user(
            user_id=request.user_id,
            full_name=data.get('full_name'),
            organization=data.get('organization')
        )

        if not success:
            return error_response('Failed to update profile', 400)

        return success_response(message='Profile updated successfully')

    return auth_bp

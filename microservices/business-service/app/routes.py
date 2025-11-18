"""
Routes for business service
"""
from flask import Blueprint, request
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))
from response import success_response, error_response, validation_error
from auth_middleware import token_required

business_bp = Blueprint('business', __name__)


def init_routes(business_model):
    """Initialize routes with business model"""

    @business_bp.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return success_response(data={'status': 'healthy', 'service': 'business-service'})

    @business_bp.route('/businesses', methods=['POST'])
    @token_required
    def create_business():
        """Create a new business"""
        data = request.get_json()

        # Validate input
        required_fields = ['name', 'category', 'address']
        errors = {}

        for field in required_fields:
            if not data.get(field):
                errors[field] = f'{field} is required'

        if errors:
            return validation_error(errors)

        # Create business
        business_id, error = business_model.create_business(
            name=data['name'],
            description=data.get('description', ''),
            category=data['category'],
            address=data['address'],
            owner_id=request.user_id
        )

        if error:
            return error_response(error, 400)

        return success_response(
            data={'business_id': business_id},
            message='Business created successfully',
            status_code=201
        )

    @business_bp.route('/businesses', methods=['GET'])
    def get_all_businesses():
        """Get all businesses"""
        businesses = business_model.get_all_businesses()
        return success_response(data={'businesses': businesses})

    @business_bp.route('/businesses/<int:business_id>', methods=['GET'])
    def get_business(business_id):
        """Get business by ID"""
        business = business_model.get_business_by_id(business_id)

        if not business:
            return error_response('Business not found', 404)

        return success_response(data={'business': business})

    @business_bp.route('/businesses/owner/<int:owner_id>', methods=['GET'])
    @token_required
    def get_businesses_by_owner(owner_id):
        """Get businesses by owner"""
        # Verify user is requesting their own businesses
        if request.user_id != owner_id:
            return error_response('Unauthorized', 403)

        businesses = business_model.get_businesses_by_owner(owner_id)
        return success_response(data={'businesses': businesses})

    @business_bp.route('/businesses/my-businesses', methods=['GET'])
    @token_required
    def get_my_businesses():
        """Get businesses owned by the authenticated user"""
        businesses = business_model.get_businesses_by_owner(request.user_id)
        return success_response(data={'businesses': businesses})

    @business_bp.route('/businesses/<int:business_id>', methods=['PUT'])
    @token_required
    def update_business(business_id):
        """Update business information"""
        data = request.get_json()

        success, error = business_model.update_business(
            business_id=business_id,
            owner_id=request.user_id,
            name=data.get('name'),
            description=data.get('description'),
            category=data.get('category'),
            address=data.get('address')
        )

        if not success:
            return error_response(error or 'Failed to update business', 400)

        return success_response(message='Business updated successfully')

    @business_bp.route('/businesses/<int:business_id>', methods=['DELETE'])
    @token_required
    def delete_business(business_id):
        """Delete a business"""
        success, error = business_model.delete_business(business_id, request.user_id)

        if not success:
            return error_response(error or 'Failed to delete business', 400)

        return success_response(message='Business deleted successfully')

    @business_bp.route('/businesses/<int:business_id>/stats', methods=['GET'])
    def get_business_stats(business_id):
        """Get business statistics"""
        stats = business_model.get_business_stats(business_id)

        if not stats:
            return error_response('Business not found', 404)

        return success_response(data={'stats': stats})

    return business_bp

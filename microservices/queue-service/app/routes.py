"""
Routes for queue service
"""
from flask import Blueprint, request
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))
from response import success_response, error_response, validation_error
from auth_middleware import token_required

queue_bp = Blueprint('queue', __name__)


def init_routes(queue_model, ticket_model):
    """Initialize routes with models"""

    @queue_bp.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return success_response(data={'status': 'healthy', 'service': 'queue-service'})

    # ==================== Queue Management Routes ====================

    @queue_bp.route('/queues', methods=['POST'])
    def create_queue():
        """Create a new queue (typically called by Business Service)"""
        data = request.get_json()

        # Validate input
        if not data.get('business_id') or not data.get('name'):
            return validation_error({'business_id': 'Required', 'name': 'Required'})

        queue_id, error = queue_model.create_queue(
            business_id=data['business_id'],
            name=data['name'],
            avg_service_time=data.get('avg_service_time', 5)
        )

        if error:
            return error_response(error, 400)

        return success_response(
            data={'queue_id': queue_id},
            message='Queue created successfully',
            status_code=201
        )

    @queue_bp.route('/queues/<int:queue_id>', methods=['GET'])
    def get_queue(queue_id):
        """Get queue details"""
        queue = queue_model.get_queue_by_id(queue_id)

        if not queue:
            return error_response('Queue not found', 404)

        # Add queue size and active tickets
        queue['size'] = queue_model.get_queue_size(queue_id)
        queue['active_tickets'] = queue_model.get_active_tickets(queue_id)

        return success_response(data={'queue': queue})

    @queue_bp.route('/queues/business/<int:business_id>', methods=['GET'])
    def get_business_queues(business_id):
        """Get all queues for a business"""
        queues = queue_model.get_queues_by_business(business_id)

        # Add size to each queue
        for queue in queues:
            queue['size'] = queue_model.get_queue_size(queue['id'])

        return success_response(data={'queues': queues})

    @queue_bp.route('/queues/<int:queue_id>', methods=['PUT'])
    @token_required
    def update_queue(queue_id):
        """Update queue information"""
        data = request.get_json()

        success = queue_model.update_queue(
            queue_id=queue_id,
            name=data.get('name'),
            avg_service_time=data.get('avg_service_time'),
            is_active=data.get('is_active')
        )

        if not success:
            return error_response('Failed to update queue', 400)

        return success_response(message='Queue updated successfully')

    @queue_bp.route('/queues/<int:queue_id>', methods=['DELETE'])
    @token_required
    def delete_queue(queue_id):
        """Delete (deactivate) a queue"""
        success = queue_model.delete_queue(queue_id)

        if not success:
            return error_response('Failed to delete queue', 400)

        return success_response(message='Queue deleted successfully')

    # ==================== Ticket Management Routes ====================

    @queue_bp.route('/queues/<int:queue_id>/join', methods=['POST'])
    @token_required
    def join_queue(queue_id):
        """Join a queue"""
        # Check if user already has an active ticket
        existing_ticket = ticket_model.get_user_active_ticket(request.user_id)
        if existing_ticket:
            return error_response('You already have an active ticket in another queue', 400)

        # Verify queue exists
        queue = queue_model.get_queue_by_id(queue_id)
        if not queue:
            return error_response('Queue not found', 404)

        # Create ticket
        ticket_id, position, error = ticket_model.create_ticket(queue_id, request.user_id)

        if error:
            return error_response(error, 400)

        # Calculate ETA
        eta = ticket_model.calculate_eta(queue_id, position)

        return success_response(
            data={
                'ticket_id': ticket_id,
                'position': position,
                'eta': eta,
                'queue_name': queue['name']
            },
            message='Joined queue successfully',
            status_code=201
        )

    @queue_bp.route('/tickets/<ticket_id>', methods=['GET'])
    @token_required
    def get_ticket(ticket_id):
        """Get ticket details"""
        ticket = ticket_model.get_ticket_by_id(ticket_id)

        if not ticket:
            return error_response('Ticket not found', 404)

        # Verify ownership
        if ticket['user_id'] != request.user_id:
            return error_response('Unauthorized', 403)

        # Add ETA if still active
        if ticket['status'] == 'active':
            ticket['eta'] = ticket_model.calculate_eta(ticket['queue_id'], ticket['position'])

        return success_response(data={'ticket': ticket})

    @queue_bp.route('/tickets/<ticket_id>/cancel', methods=['POST'])
    @token_required
    def cancel_ticket(ticket_id):
        """Cancel a ticket (leave queue)"""
        success, error = ticket_model.cancel_ticket(ticket_id, request.user_id)

        if not success:
            return error_response(error or 'Failed to cancel ticket', 400)

        return success_response(message='Ticket cancelled successfully')

    @queue_bp.route('/queues/<int:queue_id>/serve-next', methods=['POST'])
    @token_required
    def serve_next(queue_id):
        """Serve next customer in queue"""
        ticket, error = ticket_model.serve_next_customer(queue_id)

        if error:
            return error_response(error, 400)

        return success_response(
            data={'served_ticket': ticket},
            message='Customer served successfully'
        )

    @queue_bp.route('/tickets/my-history', methods=['GET'])
    @token_required
    def get_my_history():
        """Get user's queue history"""
        limit = request.args.get('limit', 50, type=int)
        history = ticket_model.get_user_history(request.user_id, limit)

        return success_response(data={'history': history})

    @queue_bp.route('/tickets/my-active', methods=['GET'])
    @token_required
    def get_my_active_ticket():
        """Get user's active ticket if any"""
        ticket = ticket_model.get_user_active_ticket(request.user_id)

        if not ticket:
            return success_response(data={'ticket': None}, message='No active ticket')

        # Add ETA
        ticket['eta'] = ticket_model.calculate_eta(ticket['queue_id'], ticket['position'])

        return success_response(data={'ticket': ticket})

    return queue_bp

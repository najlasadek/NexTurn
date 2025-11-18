"""
Frontend Service - API Gateway and Template Server
This service serves the frontend HTML templates and proxies requests to microservices
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import requests
import os
import sys

# Add parent directory to path for config imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.config import Config

# Determine template and static folder paths
# In Docker container, they are at /app/templates and /app/static
# In local development, they might be at ../../templates and ../../static
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')

# Check if running in Docker (absolute paths exist)
if os.path.exists('/app/templates'):
    TEMPLATE_FOLDER = '/app/templates'
    STATIC_FOLDER = '/app/static'

app = Flask(__name__,
            template_folder=TEMPLATE_FOLDER,
            static_folder=STATIC_FOLDER)
app.config.from_object(Config)
CORS(app, origins=Config.CORS_ORIGINS)

# Service URLs
AUTH_SERVICE = Config.AUTH_SERVICE_URL
BUSINESS_SERVICE = Config.BUSINESS_SERVICE_URL
QUEUE_SERVICE = Config.QUEUE_SERVICE_URL


def proxy_request(service_url, path, method='GET', data=None, headers=None):
    """
    Proxy requests to microservices
    """
    url = f"{service_url}{path}"

    # Prepare headers
    request_headers = {}
    if headers:
        request_headers.update(headers)

    # Forward Authorization header from original request if present
    auth_header = request.headers.get('Authorization')
    if auth_header:
        request_headers['Authorization'] = auth_header
    # Otherwise, add authorization token from session if available
    elif 'token' in session:
        request_headers['Authorization'] = f"Bearer {session['token']}"

    # Forward Content-Type from original request
    if request.content_type:
        request_headers['Content-Type'] = request.content_type

    try:
        if method == 'GET':
            response = requests.get(url, headers=request_headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=request_headers, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=request_headers, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, headers=request_headers, timeout=10)
        else:
            return jsonify({'success': False, 'message': 'Invalid method'}), 400

        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'message': f'Service unavailable: {str(e)}'}), 503


# ============================================================================
# TEMPLATE ROUTES - Serve HTML Pages
# ============================================================================

@app.route('/')
@app.route('/home')
def index():
    """Home page"""
    return render_template('index.html')

# Alias for 'home' route name
app.add_url_rule('/home', 'home', index)

@app.route('/login', methods=['GET', 'POST'], endpoint='login')
def login_page():
    """Login page"""
    if request.method == 'POST':
        # Handle login form submission - proxy to auth service
        data = request.get_json() or request.form.to_dict()
        response, status_code = proxy_request(AUTH_SERVICE, '/auth/login', method='POST', data=data)

        # Store token in session if login successful
        if status_code == 200 and response.get('success'):
            session['token'] = response['data']['token']
            session['user'] = response['data']['user']

        return jsonify(response), status_code

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'], endpoint='signup')
def signup_page():
    """Signup page"""
    if request.method == 'POST':
        # Handle signup form submission - proxy to auth service
        data = request.get_json() or request.form.to_dict()
        return proxy_request(AUTH_SERVICE, '/auth/signup', method='POST', data=data)

    return render_template('signup.html')

@app.route('/businesses', endpoint='businesses_list')
def businesses_list():
    """Businesses list page"""
    return render_template('businesses_list.html')

@app.route('/register-business', endpoint='register_business')
def register_business_page():
    """Register business page"""
    return render_template('register_business.html')

@app.route('/business-dashboard', endpoint='business_dashboard')
def business_dashboard():
    """Business dashboard page"""
    return render_template('business_dashboard.html')

@app.route('/business-queues', endpoint='business_queues')
def business_queues():
    """Business queues page"""
    return render_template('business_queues.html')

@app.route('/manage-queue')
def manage_queue():
    """Manage queue page"""
    return render_template('manage_queue.html')

@app.route('/ticket')
def ticket_page():
    """Ticket page"""
    return render_template('ticket.html')

@app.route('/queue-history', endpoint='queue_history_page')
def queue_history():
    """Queue history page"""
    return render_template('queue_history.html')

@app.route('/feedback-form')
def feedback_form():
    """Feedback form page"""
    return render_template('feedback_form.html')

@app.route('/feedback-list')
def feedback_list():
    """Feedback list page"""
    return render_template('feedback_list.html')


# ============================================================================
# API GATEWAY ROUTES - Proxy to Microservices
# ============================================================================

# ---------- Authentication Service Routes ----------

@app.route('/auth/signup', methods=['POST'])
def auth_signup():
    """Proxy signup request to auth service"""
    data = request.get_json()
    return proxy_request(AUTH_SERVICE, '/auth/signup', method='POST', data=data)

@app.route('/auth/login', methods=['POST'])
def auth_login():
    """Proxy login request to auth service and store token in session"""
    data = request.get_json()
    response, status_code = proxy_request(AUTH_SERVICE, '/auth/login', method='POST', data=data)

    # Store token in session if login successful
    if status_code == 200 and response.get('success'):
        session['token'] = response['data']['token']
        session['user'] = response['data']['user']

    return jsonify(response), status_code

@app.route('/auth/logout', methods=['POST'])
def auth_logout():
    """Logout and clear session"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200

@app.route('/logout', methods=['GET'], endpoint='logout')
def logout():
    """Logout page redirect"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/join-queue/<int:queue_id>', methods=['GET', 'POST'])
def join_queue_page(queue_id):
    """Join queue page"""
    return render_template('businesses_list.html')

# Additional routes for template compatibility
@app.route('/join-queue', methods=['GET'], endpoint='join_queue')
def join_queue_list():
    """Join queue list page"""
    return redirect(url_for('businesses_list'))

@app.route('/business/<int:business_id>/queues')
def business_queues_detail(business_id):
    """Business queues detail page"""
    return render_template('business_queues.html')

@app.route('/business/<int:business_id>/queue/<int:queue_id>')
def manage_business_queue(business_id, queue_id):
    """Manage specific business queue"""
    return render_template('manage_queue.html')

@app.route('/business/queue/<int:queue_id>/next', methods=['POST'])
def serve_next_api(queue_id):
    """Serve next customer API"""
    data = request.get_json() or {}
    return proxy_request(QUEUE_SERVICE, f'/api/queues/{queue_id}/serve-next', method='POST', data=data)

@app.route('/leave-queue', methods=['POST'], endpoint='leave_queue')
def leave_queue():
    """Leave queue"""
    data = request.get_json() or {}
    ticket_id = data.get('ticket_id')
    if ticket_id:
        return proxy_request(QUEUE_SERVICE, f'/api/tickets/{ticket_id}/cancel', method='POST', data=data)
    return jsonify({'success': False, 'message': 'No ticket_id provided'}), 400

@app.route('/ticket/alerts', methods=['POST'])
def ticket_alerts():
    """Ticket alerts endpoint"""
    return jsonify({'success': True, 'message': 'Alerts enabled'}), 200

@app.route('/feedback/<int:business_id>', methods=['GET', 'POST'])
def feedback(business_id):
    """Feedback page"""
    if request.method == 'GET':
        return render_template('feedback_form.html')
    # POST - submit feedback (placeholder)
    return jsonify({'success': True, 'message': 'Feedback submitted'}), 200

@app.route('/business/<int:business_id>/feedback-list')
def business_feedback_list(business_id):
    """Business feedback list"""
    return render_template('feedback_list.html')

@app.route('/favicon.ico')
def favicon():
    """Favicon"""
    return redirect(url_for('static', filename='logo.png'))

# ============================================================================
# ROUTE NAME ALIASES - Template Compatibility Layer
# ============================================================================
# Register additional endpoint names for existing routes so url_for() works

# The @app.route decorators above create routes with endpoint names matching function names
# We need to add ADDITIONAL endpoints pointing to the same URLs but with different names

# Cannot add duplicate routes, but we can make the route decorator use specific endpoint names
# Actually, the decorators already created the routes. Let's just ensure the endpoint names match what templates expect.

# Add update_alerts route stub
@app.route('/update-alerts', methods=['POST'])
def update_alerts():
    """Update alerts endpoint"""
    return jsonify({'success': True, 'message': 'Alerts updated'}), 200

@app.route('/auth/verify', methods=['GET'])
def auth_verify():
    """Verify token"""
    return proxy_request(AUTH_SERVICE, '/auth/verify', method='GET')

@app.route('/auth/profile', methods=['GET', 'PUT'])
def auth_profile():
    """Get or update user profile"""
    if request.method == 'GET':
        return proxy_request(AUTH_SERVICE, '/auth/profile', method='GET')
    else:
        data = request.get_json()
        return proxy_request(AUTH_SERVICE, '/auth/profile', method='PUT', data=data)

@app.route('/auth/health', methods=['GET'])
def auth_health():
    """Check auth service health"""
    return proxy_request(AUTH_SERVICE, '/auth/health', method='GET')


# ---------- Business Service Routes ----------

@app.route('/api/businesses', methods=['GET', 'POST'])
def businesses():
    """Get all businesses or create new business"""
    if request.method == 'GET':
        return proxy_request(BUSINESS_SERVICE, '/api/businesses', method='GET')
    else:
        data = request.get_json()
        return proxy_request(BUSINESS_SERVICE, '/api/businesses', method='POST', data=data)

@app.route('/api/businesses/<int:business_id>', methods=['GET', 'PUT', 'DELETE'])
def business_detail(business_id):
    """Get, update, or delete business"""
    if request.method == 'GET':
        return proxy_request(BUSINESS_SERVICE, f'/api/businesses/{business_id}', method='GET')
    elif request.method == 'PUT':
        data = request.get_json()
        return proxy_request(BUSINESS_SERVICE, f'/api/businesses/{business_id}', method='PUT', data=data)
    else:
        return proxy_request(BUSINESS_SERVICE, f'/api/businesses/{business_id}', method='DELETE')

@app.route('/api/businesses/my-businesses', methods=['GET'])
def my_businesses():
    """Get user's businesses"""
    return proxy_request(BUSINESS_SERVICE, '/api/businesses/my-businesses', method='GET')

@app.route('/api/businesses/<int:business_id>/stats', methods=['GET'])
def business_stats(business_id):
    """Get business statistics"""
    return proxy_request(BUSINESS_SERVICE, f'/api/businesses/{business_id}/stats', method='GET')

@app.route('/api/health', methods=['GET'])
def business_health():
    """Check business service health"""
    return proxy_request(BUSINESS_SERVICE, '/api/health', method='GET')


# ---------- Queue Service Routes ----------

@app.route('/api/queues', methods=['POST'])
def create_queue():
    """Create new queue"""
    data = request.get_json()
    return proxy_request(QUEUE_SERVICE, '/api/queues', method='POST', data=data)

@app.route('/api/queues/<int:queue_id>', methods=['GET', 'PUT', 'DELETE'])
def queue_detail(queue_id):
    """Get, update, or delete queue"""
    if request.method == 'GET':
        return proxy_request(QUEUE_SERVICE, f'/api/queues/{queue_id}', method='GET')
    elif request.method == 'PUT':
        data = request.get_json()
        return proxy_request(QUEUE_SERVICE, f'/api/queues/{queue_id}', method='PUT', data=data)
    else:
        return proxy_request(QUEUE_SERVICE, f'/api/queues/{queue_id}', method='DELETE')

@app.route('/api/queues/business/<int:business_id>', methods=['GET'])
def business_queues_api(business_id):
    """Get queues for a business"""
    return proxy_request(QUEUE_SERVICE, f'/api/queues/business/{business_id}', method='GET')

@app.route('/api/queues/<int:queue_id>/join', methods=['POST'])
def join_queue_api(queue_id):
    """Join a queue API"""
    data = request.get_json() or {}
    return proxy_request(QUEUE_SERVICE, f'/api/queues/{queue_id}/join', method='POST', data=data)

@app.route('/api/queues/<int:queue_id>/serve-next', methods=['POST'])
def serve_next(queue_id):
    """Serve next customer in queue"""
    data = request.get_json() or {}
    return proxy_request(QUEUE_SERVICE, f'/api/queues/{queue_id}/serve-next', method='POST', data=data)

@app.route('/api/tickets/<ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """Get ticket details"""
    return proxy_request(QUEUE_SERVICE, f'/api/tickets/{ticket_id}', method='GET')

@app.route('/api/tickets/<ticket_id>/cancel', methods=['POST'])
def cancel_ticket(ticket_id):
    """Cancel a ticket"""
    data = request.get_json() or {}
    return proxy_request(QUEUE_SERVICE, f'/api/tickets/{ticket_id}/cancel', method='POST', data=data)

@app.route('/api/tickets/my-active', methods=['GET'])
def my_active_ticket():
    """Get user's active ticket"""
    return proxy_request(QUEUE_SERVICE, '/api/tickets/my-active', method='GET')

@app.route('/api/tickets/my-history', methods=['GET'])
def my_ticket_history():
    """Get user's ticket history"""
    return proxy_request(QUEUE_SERVICE, '/api/tickets/my-history', method='GET')

@app.route('/api/queue-health', methods=['GET'])
def queue_health():
    """Check queue service health"""
    return proxy_request(QUEUE_SERVICE, '/api/health', method='GET')


# ---------- Gateway Health Check ----------

@app.route('/health', methods=['GET'])
def gateway_health():
    """Gateway health check"""
    return jsonify({
        'success': True,
        'data': {
            'service': 'frontend-gateway',
            'status': 'healthy',
            'microservices': {
                'auth': AUTH_SERVICE,
                'business': BUSINESS_SERVICE,
                'queue': QUEUE_SERVICE
            }
        }
    }), 200


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'message': 'Endpoint not found'}), 404
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'success': False, 'message': 'Internal server error'}), 500


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    print(f"🌐 Frontend Gateway Service starting on port {Config.FRONTEND_SERVICE_PORT}...")
    print(f"📡 Microservices Configuration:")
    print(f"   - Auth Service: {AUTH_SERVICE}")
    print(f"   - Business Service: {BUSINESS_SERVICE}")
    print(f"   - Queue Service: {QUEUE_SERVICE}")

    app.run(
        host='0.0.0.0',
        port=Config.FRONTEND_SERVICE_PORT,
        debug=Config.DEBUG
    )

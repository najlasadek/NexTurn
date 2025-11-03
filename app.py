from flask import Flask, render_template, session, redirect, url_for, flash, request, send_from_directory
from datetime import datetime
import uuid
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_ROOT, 'users.db')

app = Flask(__name__)
app.config['STATIC_FOLDER'] = os.path.join(APP_ROOT, 'static')
app.static_folder = 'static'
app.template_folder = 'templates'
app.secret_key = 'your-secret-key'  # TODO: change me

# -------------------- USER ACCOUNT STORAGE (SQLite) --------------------
def init_db():
    os.makedirs(APP_ROOT, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            organization TEXT,
            user_type TEXT DEFAULT 'customer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Businesses table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS businesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            address TEXT,
            owner_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
    """)

    # Queues table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS queues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            avg_service_time INTEGER DEFAULT 5,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (business_id) REFERENCES businesses(id)
        )
    """)

    # Queue history table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS queue_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            queue_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            ticket_id TEXT NOT NULL,
            position INTEGER,
            join_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            leave_time TIMESTAMP,
            wait_time INTEGER,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (queue_id) REFERENCES queues(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Feedback table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            business_id INTEGER NOT NULL,
            rating INTEGER,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (business_id) REFERENCES businesses(id)
        )
    """)

    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, full_name, email, password_hash, organization FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'full_name': row[1], 'email': row[2], 'password_hash': row[3], 'organization': row[4]}
    return None

def create_user(full_name, email, password, organization):
    if get_user_by_email(email):
        return False, 'Email already registered.'
    pw_hash = generate_password_hash(password)
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (full_name, email, password_hash, organization) VALUES (?,?,?,?)",
            (full_name, email, pw_hash, organization)
        )
        conn.commit()
        conn.close()
        return True, None
    except sqlite3.IntegrityError:
        return False, 'Email already registered.'
    except Exception as e:
        return False, str(e)

def verify_user(email, password):
    user = get_user_by_email(email)
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

init_db()

# -------------------- Queue domain (unchanged) --------------------
class Ticket:
    def __init__(self, id, position):
        self.id = id
        self.position = position
        self.alerts_enabled = False
        self.alert_threshold = 0
        self.alert_channels = []
        self.email = None
        self.eta = 0
        self.alerts_sent = False

class Queue:
    def __init__(self):
        self.tickets = {}
        self.position_counter = 0
    
    def join_queue(self, email=None):
        if 'ticket_id' in session and session['ticket_id'] in self.tickets:
            return None
        ticket_id = str(uuid.uuid4())
        self.position_counter += 1
        ticket = Ticket(ticket_id, self.position_counter)
        ticket.email = email
        ticket.eta = self.calculate_eta(ticket.position)
        self.tickets[ticket_id] = ticket
        return ticket

    def leave_queue(self, ticket_id):
        if ticket_id in self.tickets:
            removed_position = self.tickets[ticket_id].position
            del self.tickets[ticket_id]
            self.recalculate_positions(removed_position)
            return True
        return False
    
    def get_estimated_wait_time(self, position):
        avg_service_time_per_person = 5  # minutes
        remaining_people = max(position - 1, 0)
        return remaining_people * avg_service_time_per_person

    def calculate_eta(self, position):
        minutes = self.get_estimated_wait_time(position)
        return minutes

    def recalculate_positions(self, start_position):
        for ticket in self.tickets.values():
            if ticket.position > start_position:
                ticket.position -= 1
                ticket.eta = self.calculate_eta(ticket.position)

    def update_alerts(self, ticket_id, enabled, threshold, channels):
        if ticket_id in self.tickets:
            ticket = self.tickets[ticket_id]
            ticket.alerts_enabled = enabled
            ticket.alert_threshold = threshold
            ticket.alert_channels = channels
            return True
        return False

    def check_and_send_alerts(self):
        for ticket in self.tickets.values():
            if (ticket.alerts_enabled and 
                ticket.position <= ticket.alert_threshold and 
                not ticket.alerts_sent):
                self.send_alert(ticket)
                ticket.alerts_sent = True

    def send_alert(self, ticket):
        message = f"Your turn is approaching! You are position #{ticket.position} in the queue."
        # implement browser/email alerts if needed
        pass

queue = Queue()

# -------------------- Auth helpers --------------------
def require_login():
    return 'user_id' in session

# -------------------- Routes --------------------
@app.route('/')
def home():
    if not require_login():
        return redirect(url_for('login'))
    # Pass user to template if you want to greet
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'logo.png')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If already signed in, go home
    if request.method == 'GET' and require_login():
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = verify_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_name'] = user['full_name']
            flash('Welcome back!', 'success')
            return redirect(url_for('home'))
        else:
            # <- Requirement #3: explicit error if email or password is wrong
            flash('The email or password is incorrect.', 'error')
            return render_template('login.html'), 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been signed out.', 'success')
    # <- Requirement #1: after pressing logout, go "home" (which will show login if unauthenticated)
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('fullname', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        organization = request.form.get('organization', '').strip()

        # <- Requirement #2: Confirm Password must match
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html'), 400

        ok, err = create_user(full_name, email, password, organization)
        if ok:
            flash('Account created. Please sign in.', 'success')
            return redirect(url_for('login'))
        else:
            flash(err or 'Could not create account.', 'error')
            return render_template('signup.html'), 400

    return render_template('signup.html')

@app.route('/businesses')
def businesses_list():
    if not require_login():
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get all businesses with their active queues
    cur.execute("""
        SELECT b.id, b.name, b.description, b.category, b.address,
               COUNT(DISTINCT q.id) as queue_count
        FROM businesses b
        LEFT JOIN queues q ON b.id = q.business_id AND q.is_active = 1
        GROUP BY b.id
    """)
    businesses = [{'id': row[0], 'name': row[1], 'description': row[2],
                   'category': row[3], 'address': row[4], 'queue_count': row[5]}
                  for row in cur.fetchall()]

    conn.close()
    return render_template('businesses_list.html', businesses=businesses)

@app.route('/join-queue/<int:queue_id>')
def join_queue_by_id(queue_id):
    if not require_login():
        return redirect(url_for('login'))

    if 'ticket_id' in session and session['ticket_id'] in queue.tickets:
        flash('You are already in a queue. Leave your current queue first.', 'error')
        return redirect(url_for('show_ticket'))

    user_id = session.get('user_id')
    user_email = session.get('user_email')

    # Create ticket in memory
    ticket = queue.join_queue(user_email)
    if ticket:
        # Save to database
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO queue_history (queue_id, user_id, ticket_id, position, status)
            VALUES (?, ?, ?, ?, 'active')
        """, (queue_id, user_id, ticket.id, ticket.position))
        conn.commit()
        conn.close()

        session['ticket_id'] = ticket.id
        session['queue_id'] = queue_id
        flash('You have joined the queue successfully!', 'success')
        return redirect(url_for('show_ticket'))

    flash('Failed to join queue.', 'error')
    return redirect(url_for('businesses_list'))

@app.route('/join-queue')
def join_queue():
    # Redirect to businesses list for now
    return redirect(url_for('businesses_list'))

@app.route('/business/<int:business_id>/queues')
def business_queues(business_id):
    if not require_login():
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get business info
    cur.execute("SELECT name, description, category, address FROM businesses WHERE id = ?", (business_id,))
    row = cur.fetchone()
    if not row:
        flash('Business not found', 'error')
        return redirect(url_for('businesses_list'))

    business = {'id': business_id, 'name': row[0], 'description': row[1],
                'category': row[2], 'address': row[3]}

    # Get active queues
    cur.execute("""
        SELECT q.id, q.name, q.avg_service_time,
               COUNT(qh.id) as current_size
        FROM queues q
        LEFT JOIN queue_history qh ON q.id = qh.queue_id AND qh.status = 'active'
        WHERE q.business_id = ? AND q.is_active = 1
        GROUP BY q.id
    """, (business_id,))

    queues = [{'id': row[0], 'name': row[1], 'avg_service_time': row[2],
               'current_size': row[3], 'estimated_wait': row[2] * row[3]}
              for row in cur.fetchall()]

    conn.close()
    return render_template('business_queues.html', business=business, queues=queues)

@app.route('/queue-history')
def queue_history_page():
    if not require_login():
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT qh.id, qh.ticket_id, qh.position, qh.join_time, qh.leave_time,
               qh.wait_time, qh.status, q.name as queue_name, b.name as business_name
        FROM queue_history qh
        JOIN queues q ON qh.queue_id = q.id
        JOIN businesses b ON q.business_id = b.id
        WHERE qh.user_id = ?
        ORDER BY qh.join_time DESC
        LIMIT 50
    """, (user_id,))

    history = [{'id': row[0], 'ticket_id': row[1], 'position': row[2],
                'join_time': row[3], 'leave_time': row[4], 'wait_time': row[5],
                'status': row[6], 'queue_name': row[7], 'business_name': row[8]}
               for row in cur.fetchall()]

    conn.close()
    return render_template('queue_history.html', history=history)

@app.route('/ticket')
def show_ticket():
    if not require_login():
        return redirect(url_for('login'))
    if 'ticket_id' not in session or session['ticket_id'] not in queue.tickets:
        return redirect(url_for('home'))
    
    ticket = queue.tickets[session['ticket_id']]
    ticket_data = {
        'id': ticket.id,
        'position': ticket.position,
        'eta': ticket.eta,
        'alerts_enabled': ticket.alerts_enabled,
        'alert_threshold': ticket.alert_threshold,
        'alert_channels': ticket.alert_channels
    }
    return render_template('ticket.html', ticket=ticket_data)

@app.route('/ticket/alerts', methods=['POST'])
def update_alerts():
    if not require_login():
        return redirect(url_for('login'))
    if 'ticket_id' not in session:
        return redirect(url_for('home'))

    ticket_id = session['ticket_id']
    enabled = request.form.get('enabled') == 'true'
    threshold = int(request.form.get('threshold', 3))
    channels = request.form.getlist('channels')

    if queue.update_alerts(ticket_id, enabled, threshold, channels):
        flash('Alert preferences updated successfully', 'success')
    else:
        flash('Failed to update alert preferences', 'error')

    return redirect(url_for('show_ticket'))

@app.route('/leave-queue', methods=['POST'])
def leave_queue():
    if not require_login():
        return redirect(url_for('login'))

    if 'ticket_id' in session:
        ticket_id = session['ticket_id']
        if queue.leave_queue(ticket_id):
            # Record in database
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                UPDATE queue_history
                SET leave_time = CURRENT_TIMESTAMP,
                    status = 'cancelled',
                    wait_time = (strftime('%s', 'now') - strftime('%s', join_time)) / 60
                WHERE ticket_id = ? AND status = 'active'
            """, (ticket_id,))
            conn.commit()
            conn.close()

            session.pop('ticket_id', None)
            flash('You have left the queue successfully.', 'success')
        else:
            flash('Failed to leave queue.', 'error')

    return redirect(url_for('home'))

@app.route('/business/dashboard')
def business_dashboard():
    if not require_login():
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get businesses owned by this user
    cur.execute("""
        SELECT id, name, description, category, address, created_at
        FROM businesses
        WHERE owner_id = ?
    """, (user_id,))
    businesses = [{'id': row[0], 'name': row[1], 'description': row[2],
                   'category': row[3], 'address': row[4], 'created_at': row[5]}
                  for row in cur.fetchall()]

    # Get queues for each business
    for business in businesses:
        cur.execute("""
            SELECT id, name, avg_service_time, is_active
            FROM queues
            WHERE business_id = ?
        """, (business['id'],))
        business['queues'] = [{'id': row[0], 'name': row[1],
                               'avg_service_time': row[2], 'is_active': row[3]}
                             for row in cur.fetchall()]

    conn.close()
    return render_template('business_dashboard.html', businesses=businesses)

@app.route('/business/register', methods=['GET', 'POST'])
def register_business():
    if not require_login():
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        address = request.form.get('address', '').strip()
        user_id = session.get('user_id')

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO businesses (name, description, category, address, owner_id)
                VALUES (?, ?, ?, ?, ?)
            """, (name, description, category, address, user_id))
            business_id = cur.lastrowid

            # Create a default queue
            cur.execute("""
                INSERT INTO queues (business_id, name, avg_service_time, is_active)
                VALUES (?, ?, ?, ?)
            """, (business_id, 'Main Queue', 5, 1))

            conn.commit()
            conn.close()

            flash('Business registered successfully!', 'success')
            return redirect(url_for('business_dashboard'))
        except Exception as e:
            flash(f'Error registering business: {str(e)}', 'error')
            return render_template('register_business.html'), 400

    return render_template('register_business.html')

@app.route('/business/<int:business_id>/queue/<int:queue_id>')
def manage_queue(business_id, queue_id):
    if not require_login():
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Verify ownership
    cur.execute("SELECT owner_id FROM businesses WHERE id = ?", (business_id,))
    row = cur.fetchone()
    if not row or row[0] != session.get('user_id'):
        flash('Unauthorized access', 'error')
        return redirect(url_for('home'))

    # Get queue info
    cur.execute("""
        SELECT q.id, q.name, q.avg_service_time, q.is_active, b.name as business_name
        FROM queues q
        JOIN businesses b ON q.business_id = b.id
        WHERE q.id = ? AND q.business_id = ?
    """, (queue_id, business_id))
    row = cur.fetchone()
    if not row:
        flash('Queue not found', 'error')
        return redirect(url_for('business_dashboard'))

    queue_info = {
        'id': row[0], 'name': row[1], 'avg_service_time': row[2],
        'is_active': row[3], 'business_name': row[4]
    }

    # Get active tickets
    cur.execute("""
        SELECT qh.id, qh.ticket_id, qh.position, qh.join_time, u.full_name, u.email
        FROM queue_history qh
        JOIN users u ON qh.user_id = u.id
        WHERE qh.queue_id = ? AND qh.status = 'active'
        ORDER BY qh.position
    """, (queue_id,))
    active_tickets = [{'id': row[0], 'ticket_id': row[1], 'position': row[2],
                       'join_time': row[3], 'user_name': row[4], 'user_email': row[5]}
                      for row in cur.fetchall()]

    # Get analytics
    cur.execute("""
        SELECT
            COUNT(*) as total_served,
            AVG(wait_time) as avg_wait_time,
            MAX(wait_time) as max_wait_time
        FROM queue_history
        WHERE queue_id = ? AND status = 'completed'
    """, (queue_id,))
    row = cur.fetchone()
    analytics = {
        'total_served': row[0] or 0,
        'avg_wait_time': round(row[1], 2) if row[1] else 0,
        'max_wait_time': round(row[2], 2) if row[2] else 0
    }

    conn.close()
    return render_template('manage_queue.html', queue=queue_info,
                          tickets=active_tickets, analytics=analytics)

@app.route('/business/queue/<int:queue_id>/next', methods=['POST'])
def serve_next(queue_id):
    if not require_login():
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get the first ticket in queue
    cur.execute("""
        SELECT id, ticket_id, user_id, position
        FROM queue_history
        WHERE queue_id = ? AND status = 'active'
        ORDER BY position
        LIMIT 1
    """, (queue_id,))
    row = cur.fetchone()

    if row:
        ticket_db_id, ticket_id, user_id, position = row

        # Mark as completed
        cur.execute("""
            UPDATE queue_history
            SET leave_time = CURRENT_TIMESTAMP,
                status = 'completed',
                wait_time = (strftime('%s', 'now') - strftime('%s', join_time)) / 60
            WHERE id = ?
        """, (ticket_db_id,))

        # Update positions of remaining tickets
        cur.execute("""
            UPDATE queue_history
            SET position = position - 1
            WHERE queue_id = ? AND status = 'active' AND position > ?
        """, (queue_id, position))

        # Remove from in-memory queue
        if ticket_id in queue.tickets:
            queue.leave_queue(ticket_id)

        conn.commit()
        flash('Next customer served successfully!', 'success')
    else:
        flash('No customers in queue', 'info')

    conn.close()

    # Redirect back to manage queue page
    cur = sqlite3.connect(DB_PATH).cursor()
    cur.execute("SELECT business_id FROM queues WHERE id = ?", (queue_id,))
    row = cur.fetchone()
    business_id = row[0] if row else None

    if business_id:
        return redirect(url_for('manage_queue', business_id=business_id, queue_id=queue_id))
    return redirect(url_for('business_dashboard'))

@app.route('/feedback/<int:business_id>', methods=['GET', 'POST'])
def submit_feedback(business_id):
    if not require_login():
        return redirect(url_for('login'))

    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment', '').strip()
        user_id = session.get('user_id')

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO feedback (user_id, business_id, rating, comment)
                VALUES (?, ?, ?, ?)
            """, (user_id, business_id, rating, comment))
            conn.commit()
            conn.close()

            flash('Thank you for your feedback!', 'success')
            return redirect(url_for('businesses_list'))
        except Exception as e:
            flash(f'Error submitting feedback: {str(e)}', 'error')

    # GET request - show feedback form
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name FROM businesses WHERE id = ?", (business_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        flash('Business not found', 'error')
        return redirect(url_for('businesses_list'))

    business_name = row[0]
    return render_template('feedback_form.html', business_id=business_id, business_name=business_name)

@app.route('/business/<int:business_id>/feedback-list')
def view_feedback(business_id):
    if not require_login():
        return redirect(url_for('login'))

    # Verify ownership
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT owner_id, name FROM businesses WHERE id = ?", (business_id,))
    row = cur.fetchone()

    if not row or row[0] != session.get('user_id'):
        flash('Unauthorized access', 'error')
        return redirect(url_for('home'))

    business_name = row[1]

    # Get all feedback
    cur.execute("""
        SELECT f.id, f.rating, f.comment, f.created_at, u.full_name
        FROM feedback f
        JOIN users u ON f.user_id = u.id
        WHERE f.business_id = ?
        ORDER BY f.created_at DESC
    """, (business_id,))

    feedback_list = [{'id': row[0], 'rating': row[1], 'comment': row[2],
                      'created_at': row[3], 'user_name': row[4]}
                     for row in cur.fetchall()]

    # Calculate average rating
    avg_rating = sum(f['rating'] for f in feedback_list) / len(feedback_list) if feedback_list else 0

    conn.close()
    return render_template('feedback_list.html', feedback=feedback_list,
                          avg_rating=round(avg_rating, 1), business_name=business_name,
                          business_id=business_id)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)

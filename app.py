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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            organization TEXT
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

@app.route('/join-queue')
def join_queue():
    if not require_login():
        return redirect(url_for('login'))
    if 'ticket_id' in session and session['ticket_id'] in queue.tickets:
        return redirect(url_for('show_ticket'))
    
    ticket = queue.join_queue(session.get('user_email'))
    if ticket:
        session['ticket_id'] = ticket.id
        flash('You have joined the queue successfully!')
        return redirect(url_for('show_ticket'))
    flash('Failed to join queue.')
    return redirect(url_for('home'))

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

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, session, redirect, url_for, flash, request, send_from_directory
from datetime import datetime
import uuid
import os
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['STATIC_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app.static_folder = 'static'
app.template_folder = 'templates'
app.secret_key = 'your-secret-key'

class Ticket:
    def __init__(self, id, position):
        self.id = id
        self.position = position
        self.alerts_enabled = False
        self.alert_threshold = 0
        self.alert_channels = []
        self.email = None
        self.eta = 0  # Add this field
        self.alerts_sent = False  # Add this field

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
        ticket.eta = self.calculate_eta(ticket.position)  # Calculate ETA
        self.tickets[ticket_id] = ticket
        return ticket

    def calculate_eta(self, position):
        # Implement your ETA calculation logic here
        return position * 5  # Simple example: 5 minutes per person

    def update_alerts(self, ticket_id, enabled, threshold=3, channels=None):
        if ticket_id in self.tickets:
            ticket = self.tickets[ticket_id]
            ticket.alerts_enabled = enabled
            ticket.alert_threshold = threshold
            ticket.alert_channels = channels or []
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
        if 'browser' in ticket.alert_channels:
            # Implementation for browser notification would go here
            pass
        if 'email' in ticket.alert_channels and ticket.email:
            self.send_email_alert(ticket.email, message)

    def send_email_alert(self, email, message):
        # Add your email sending logic here
        pass

queue = Queue()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'logo.jpg')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Add login logic here
        session['user'] = email
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Add signup logic here
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/join-queue')
def join_queue():
    if 'ticket_id' in session and session['ticket_id'] in queue.tickets:
        return redirect(url_for('show_ticket'))
    
    ticket = queue.join_queue(session.get('user'))
    if ticket:
        session['ticket_id'] = ticket.id  # Access id as property, not dict key
        return redirect(url_for('show_ticket'))
    return redirect(url_for('home'))

@app.route('/ticket')
def show_ticket():
    if 'ticket_id' not in session or session['ticket_id'] not in queue.tickets:
        flash('No active ticket found')
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
    if 'ticket_id' not in session:
        return redirect(url_for('home'))
    
    ticket_id = session['ticket_id']
    enabled = request.form.get('enabled') == 'true'
    threshold = int(request.form.get('threshold', 3))
    channels = request.form.getlist('channels')
    
    if queue.update_alerts(ticket_id, enabled, threshold, channels):
        flash('Alert preferences updated successfully')
    else:
        flash('Failed to update alert preferences')
    
    return redirect(url_for('show_ticket'))

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)

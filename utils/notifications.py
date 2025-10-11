import smtplib
from email.mime.text import MIMEText
import os
from typing import Dict, Any

class NotificationManager:
    def __init__(self, email_config: Dict[str, Any] = None):
        self.email_config = email_config or {
            'SMTP_SERVER': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'SMTP_PORT': int(os.getenv('SMTP_PORT', 587)),
            'SMTP_USERNAME': os.getenv('SMTP_USERNAME', ''),
            'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD', '')
        }

    def send_email(self, to_email: str, subject: str, message: str) -> bool:
        try:
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = self.email_config['SMTP_USERNAME']
            msg['To'] = to_email

            with smtplib.SMTP(self.email_config['SMTP_SERVER'], self.email_config['SMTP_PORT']) as server:
                server.starttls()
                server.login(self.email_config['SMTP_USERNAME'], self.email_config['SMTP_PASSWORD'])
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return False

    def send_browser_notification(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'type': 'notification',
            'title': 'Queue Update',
            'message': f"Your turn is approaching! You are #{ticket_data['position']} in line.",
            'icon': '/static/logo.jpg'
        }

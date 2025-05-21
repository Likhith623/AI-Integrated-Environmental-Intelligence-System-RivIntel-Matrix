from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv

load_dotenv()

def send_alert(alert_type, message, recipient):
    """
    Send emergency alerts via SMS or email.
    
    Args:
        alert_type (str): 'sms' or 'email'
        message (str): Alert message
        recipient (str): Phone number or email address
        
    Returns:
        dict: Status of the alert
    """
    if alert_type == 'sms':
        return send_sms(message, recipient)
    elif alert_type == 'email':
        return send_email(message, recipient)
    else:
        return {'error': 'Invalid alert type'}

def send_sms(message, phone_number):
    """Send SMS using Twilio"""
    try:
        client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        
        message = client.messages.create(
            body=message,
            from_=os.getenv('TWILIO_PHONE_NUMBER'),
            to=phone_number
        )
        
        return {
            'status': 'success',
            'message_sid': message.sid
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def send_email(message, email_address):
    """Send email using SendGrid"""
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        
        mail = Mail(
            from_email='alerts@rivermind.com',
            to_emails=email_address,
            subject='RiverMind Alert',
            html_content=message
        )
        
        response = sg.send(mail)
        
        return {
            'status': 'success',
            'status_code': response.status_code
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        } 
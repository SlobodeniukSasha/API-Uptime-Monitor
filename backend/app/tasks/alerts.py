import smtplib
from email.message import EmailMessage
from logging import getLogger

from backend.app.core.config import settings
from backend.app.core.celery_app import celery


logger = getLogger(__name__)

@celery.task
def send_alert_email(
        user_email: str,
        monitor_name: str,
        monitor_user_name: str,
        monitor_url: str,
        monitor_status: str,
        ai_recommendations: str,
        monitor_check_interval: int,

):
    """
    Sends an email notification to the monitor owner.
    """

    msg = EmailMessage()
    msg["From"] = settings.EMAIL_HOST_USER
    msg["To"] = user_email
    msg["Subject"] = f"Monitoring: {monitor_name} caught on change status"
    msg.set_content(
        f"""
            Hello, {monitor_user_name}!

            Site monitoring has shown a change in the result:

            Name: {monitor_name}
            URL: {monitor_url}
            New status: {monitor_status}
            
            Checked: {monitor_check_interval} seconds ago.
            
            Recommendations: {ai_recommendations}
            
            -- 
            API Health Monitor
        """)
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.send_message(msg)
        logger.info(f"Alert was sent to: {user_email}")

    except Exception as e:
        logger.exception(f"Failed to send alert: {e}")

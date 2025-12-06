"""
Custom email backend using Brevo (formerly Sendinblue) API.
This bypasses SMTP which Railway blocks.
"""
import json
import logging
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import EmailMultiAlternatives
try:
    import requests
except ImportError:
    import urllib.request
    import urllib.parse
    requests = None

logger = logging.getLogger(__name__)


class BrevoAPIBackend(BaseEmailBackend):
    """
    Email backend that sends emails via Brevo's HTTP API instead of SMTP.
    Requires EMAIL_HOST_PASSWORD to be set to Brevo API key.
    """

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects via Brevo API.
        """
        if not email_messages:
            return 0

        api_key = settings.EMAIL_HOST_PASSWORD  # Brevo API key
        if not api_key:
            logger.error("Brevo API key not configured")
            return 0

        num_sent = 0
        for message in email_messages:
            if self._send_single_message(message, api_key):
                num_sent += 1

        return num_sent

    def _send_single_message(self, message, api_key):
        """Send a single email message via Brevo API."""
        try:
            # Prepare email data for Brevo API
            email_data = {
                "sender": {
                    "email": message.from_email or settings.DEFAULT_FROM_EMAIL,
                },
                "to": [{"email": addr} for addr in message.to],
                "subject": message.subject,
                "htmlContent": self._get_html_content(message),
            }

            # Optional: add text content
            if message.body:
                email_data["textContent"] = message.body

            # Send HTTP request to Brevo API
            headers = {
                "api-key": api_key,
                "Content-Type": "application/json",
            }

            if requests:
                # Use requests library
                response = requests.post(
                    "https://api.brevo.com/v3/smtp/email",
                    json=email_data,
                    headers=headers,
                    timeout=10,
                )
                success = response.status_code == 201
                if not success:
                    logger.error(f"Brevo API error: {response.status_code} - {response.text}")
            else:
                # Fallback to urllib
                req = urllib.request.Request(
                    "https://api.brevo.com/v3/smtp/email",
                    data=json.dumps(email_data).encode('utf-8'),
                    headers=headers,
                )
                try:
                    response = urllib.request.urlopen(req, timeout=10)
                    success = response.getcode() == 201
                except urllib.error.HTTPError as e:
                    logger.error(f"Brevo API error: {e.code} - {e.read().decode()}")
                    success = False

            return success

        except Exception as e:
            logger.error(f"Failed to send email via Brevo API: {str(e)}")
            return False

    def _get_html_content(self, message):
        """Extract HTML content from message alternatives or use plain text."""
        if isinstance(message, EmailMultiAlternatives):
            for content, mimetype in message.alternatives:
                if mimetype == "text/html":
                    return content
        # Fallback: convert plain text to simple HTML
        return f"<html><body><pre>{message.body}</pre></body></html>"

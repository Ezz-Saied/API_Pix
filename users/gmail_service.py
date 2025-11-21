import base64
import pickle
from pathlib import Path

from django.conf import settings
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


def _load_service():
    """Lazy-load Gmail service so missing credentials fail with a clear error."""
    token_path = Path(settings.GOOGLE_OAUTH2_TOKEN_STORAGE)
    if not token_path.exists():
        raise FileNotFoundError(
            "Google OAuth token file not found. Upload the token to "
            f"{token_path} or set GOOGLE_OAUTH2_TOKEN_STORAGE."
        )

    with token_path.open("rb") as token_file:
        creds = pickle.load(token_file)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build("gmail", "v1", credentials=creds)


def send_email(to, subject, body, html=False):
    service = _load_service()
    message = MIMEText(body, "html" if html else "plain")
    message["to"] = to
    message["subject"] = subject
    message["from"] = "PixRevive Team <ezzezze86@gmail.com>"
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()


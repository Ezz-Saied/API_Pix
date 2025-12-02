import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Google API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Paths
CREDENTIALS_FILE = 'users/oauth/credentials.json'  
TOKEN_FILE = 'users/oauth/token.pkl'               

def main():
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )

            print(" Open this URL in your browser to authorize the app:")

            creds = flow.run_local_server(
                port=8080,
                open_browser=False
            )

        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    print("\n Token generated successfully!")
    print("Access Token:", creds.token)


if __name__ == '__main__':
    main()

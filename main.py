import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first time.
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request()) # Missing 'Request' object
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
      token.write(creds.to_json())
  try:
    service = build('gmail', 'v1', credentials=creds)
    # Call the Gmail API
    results = service.users().messages().list(userId='me', q='is:unread').execute()
    messages = results.get('messages', [])
    if not messages:
      speak("No unread messages found.")
    else:
      for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        email_content = get_email_content(msg)
        speak(email_content)
  except HttpError as error:
    print(f'An error occurred: {error}')
    speak("An error occurred while fetching emails.")

def get_email_content(message):
  headers = message['payload']['headers']
  subject = next(header['value'] for header in headers if header['name'] == 'Subject')
  from_ = next(header['value'] for header in headers if header['name'] == 'From')
  body = base64.urlsafe_b64decode(message['payload']['parts'][0]['body']['data']).decode('utf-8')
  return f"From: {from_}\nSubject: {subject}\n\n{body}"

import os.path, datetime, pytz, base64, html, re
import dateparser
from icalendar import Calendar as iCal
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/gmail.modify']

def get_services():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds), build('gmail', 'v1', credentials=creds)

def main():
    cal_service, mail_service = get_services()
    query = 'label:"VA Coaching with Big Sis" is:unread'
    print(f"Scanning label: VA Coaching with Big Sis...")

    results = mail_service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No new unread messages.")
        return

    for msg in messages:
        message = mail_service.users().messages().get(userId='me', id=msg['id']).execute()
        payload = message.get('payload', {})
        headers = payload.get('headers', [])

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "")
        snippet = html.unescape(message['snippet'])

        start_iso = None
        end_iso = None
        summary = f"Coaching: {subject}"

        # 1. ATTACHMENT CHECK
        parts = payload.get('parts', [])
        for part in parts:
            if part['mimeType'] == 'text/calendar':
                data = part['body'].get('data')
                if data:
                    decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')
                    ical = iCal.from_ical(decoded_data)
                    for component in ical.walk():
                        if component.name == "VEVENT":
                            print("Found an official invite attachment!")
                            start_iso = component.get('dtstart').dt.isoformat()
                            end_iso = component.get('dtend').dt.isoformat()
                            summary = str(component.get('summary'))

        # 2. UPDATED SUBJECT/TEXT SEARCH
        if not start_iso:
            print("Checking Subject and Text for dates...")

            if "@" in subject:
                # We extract exactly: 'Sun Feb 15, 2026 10pm'
                after_at = subject.split("@")[1]
                clean_text = after_at.split("(")[0].split("-")[0].strip()
            else:
                clean_text = f"{subject} {snippet}"

            print(f"Attempting to parse: '{clean_text}'")

            # We provide specific formats to help the library
            parsed_date = dateparser.parse(clean_text,
                date_formats=['%a %b %d, %Y %I%p', '%b %d, %Y %I%p', '%Y-%m-%d %H:%M'],
                settings={
                    'PREFER_DATES_FROM': 'future',
                    'RELATIVE_BASE': datetime.datetime.now()
                }
            )

            if parsed_date:
                local_tz = pytz.timezone('Asia/Manila')
                if parsed_date.tzinfo is None:
                    start_dt = local_tz.localize(parsed_date)
                else:
                    start_dt = parsed_date.astimezone(local_tz)

                start_iso = start_dt.isoformat()
                end_iso = (start_dt + datetime.timedelta(hours=1)).isoformat()
                print(f"Date found: {start_dt.strftime('%B %d at %I:%M %p')}")

        # 3. EXECUTE
        if start_iso:
            g_event = {
                'summary': summary,
                'start': {'dateTime': start_iso, 'timeZone': 'Asia/Manila'},
                'end': {'dateTime': end_iso, 'timeZone': 'Asia/Manila'},
            }

            try:
                cal_service.events().insert(calendarId='primary', body=g_event).execute()
                mail_service.users().messages().batchModify(userId='me', body={'removeLabelIds': ['UNREAD'], 'ids': [msg['id']]}).execute()
                print(f"✅ Success! Added: {summary}")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print(f"❌ Failure: No date found in '{subject}'")

if __name__ == '__main__':
    main()

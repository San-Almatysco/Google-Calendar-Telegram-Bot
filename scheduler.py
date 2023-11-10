from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']

def book_timeslot(event_summary, event_description, date_time, booking_time, input_email, prepod, location):

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    start_time = str(date_time + 'T' + booking_time + ':00+06:00')
    end_time = str(date_time + 'T' + str(int(booking_time[:2]) + 1) + ':00:00+06:00')

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    print('Создаю событие.')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        event = {
            'summary': str(event_summary),
            'location': str(prepod) + ' - ' + str(location),
            'description': str(event_description),
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Almaty',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Almaty',
            },
            'recurrence': [
                'RRULE:FREQ=DAILY;COUNT=2'
            ],
            'attendees': [
                {'email': 'insar@lessons.kz'},
                {'email': str(input_email)},
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Событие создано: %s' % (event.get('htmlLink')))
        return True

    else:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            if start == start_time:
                print('Это время уже занято.')
        event = {
            'summary': str(event_summary),
            'location': str(prepod) + ' - ' + str(location),
            'description': str(event_description),
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Almaty',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Almaty',
            },
            'recurrence': [
                'RRULE:FREQ=DAILY;COUNT=1'
            ],
            'attendees': [
                {'email': str(input_email)},
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Это событие уже создано: %s' % (event.get('htmlLink')))
        return True


if __name__ == '__main__':
    event_summary = 'Your Event Summary'
    event_description = 'Your Event Description'
    booking_time = '14:00'
    location = 'Your Event Location'
    input_email = 'insar@lessons.kz'
    prepod = 'Your Prepod Name'
    date_time = 'Your Date Time'
    result = book_timeslot(event_summary, event_description, date_time, booking_time, input_email, prepod, location)


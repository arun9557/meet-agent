from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import whisper
import re
import time

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_credentials():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('google_services/token.json'):
        creds = Credentials.from_authorized_user_file('google_services/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                flow = InstalledAppFlow.from_client_secrets_file(
                'google_services/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'google_services/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('google_services/token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def fetch_upcoming_events(max_results=10):
    creds = get_credentials()
    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=max_results, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return []

        return events

    except HttpError as error:
        print('An error occurred: %s' % error)
        return []

def get_next_meeting_with_link():
    """Fetches upcoming events and returns the next one with a meeting link and password."""
    events = fetch_upcoming_events()
    for event in events:
        link = None
        password = None
        
        # Simple check for meeting links. This can be improved.
        if 'hangoutLink' in event:
            link = event['hangoutLink']
        elif 'location' in event and 'zoom.us' in event.get('location', ''):
            link = event['location']
        
        # Regex to find a password in the description or location
        text_to_search = event.get('description', '') + ' ' + event.get('location', '')
        password_match = re.search(r'Password: (\w+)', text_to_search, re.IGNORECASE)
        if password_match:
            password = password_match.group(1)

        if link:
            return link, event['start']['dateTime'], event['summary'], password
            
    return None, None, None, None

def wait_and_join_meeting(link, start_time, progress_callback, password=None):
    """Joins a Zoom meeting using Selenium and enters password if provided."""
    progress_callback(f"Waiting for meeting: {link}")

    # This part can be improved to wait until the meeting time
    print(f"Joining meeting with Selenium: {link}")

    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        driver.get(link)
        
        if password:
            progress_callback("Password found, attempting to enter it.")
            # Wait for the password field to be visible and enter the password
            # This selector might need to be adjusted based on Zoom's UI
            password_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            password_field.send_keys(password)
            
            # Find and click the join button
            join_button = driver.find_element(By.ID, "joinBtn")
            join_button.click()

        progress_callback("Meeting window opened. Please join manually if needed.")
        # Keep the browser open.
    except Exception as e:
        print(f"An error occurred while trying to join the meeting: {e}")

def start_audio_recording():
    """Placeholder for starting audio recording."""
    print("Starting audio recording...")
    # This would be implemented with a library like PyAudio
    return "recorder_object"

def stop_audio_recording(recorder):
    """Placeholder for stopping audio recording."""
    print("Stopping audio recording...")

def transcribe_audio(filename="meeting_audio.wav"):
    """Transcribes the recorded audio file using Whisper."""
    if not os.path.exists(filename):
        return "Error: Audio file not found."

    print("Loading Whisper model...")
    model = whisper.load_model("base")
    print("Transcribing audio...")
    result = model.transcribe(filename)
    return result["text"] 
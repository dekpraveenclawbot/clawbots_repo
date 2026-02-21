#!/usr/bin/env python3
import argparse
import os
from datetime import datetime, timedelta, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
CREDS_FILE = "credentials.json"
TOKEN_FILE = "calendar_token.json"


def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDS_FILE):
                raise SystemExit("Missing credentials.json in workspace root.")
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def parse_args():
    p = argparse.ArgumentParser(description="Create Google Calendar events with reminders.")
    p.add_argument("--title", required=True, help="Event title")
    p.add_argument("--start", required=True, help='Start datetime, format: "YYYY-MM-DD HH:MM"')
    p.add_argument("--duration-min", type=int, default=60, help="Duration in minutes (default: 60)")
    p.add_argument("--timezone", default="UTC", help="IANA timezone, e.g. Asia/Kolkata (default: UTC)")
    p.add_argument("--calendar-id", default="primary", help="Calendar ID (default: primary)")
    p.add_argument("--location", default="", help="Optional location")
    p.add_argument("--description", default="", help="Optional description")
    p.add_argument(
        "--reminder-days",
        default="7,1",
        help="Comma-separated days-before reminders (default: 7,1)",
    )
    return p.parse_args()


def main():
    args = parse_args()

    start_local = datetime.strptime(args.start, "%Y-%m-%d %H:%M")
    end_local = start_local + timedelta(minutes=args.duration_min)

    reminder_days = []
    if args.reminder_days.strip():
        reminder_days = [int(x.strip()) for x in args.reminder_days.split(",") if x.strip()]

    overrides = []
    for d in reminder_days:
        minutes = d * 24 * 60
        overrides.append({"method": "popup", "minutes": minutes})

    event = {
        "summary": args.title,
        "location": args.location,
        "description": args.description,
        "start": {
            "dateTime": start_local.isoformat(),
            "timeZone": args.timezone,
        },
        "end": {
            "dateTime": end_local.isoformat(),
            "timeZone": args.timezone,
        },
        "reminders": {
            "useDefault": False,
            "overrides": overrides,
        },
    }

    service = get_service()
    created = service.events().insert(calendarId=args.calendar_id, body=event).execute()

    print("Event created ✅")
    print(f"Title: {created.get('summary')}")
    print(f"Start: {created.get('start', {}).get('dateTime')}")
    print(f"Link: {created.get('htmlLink')}")


if __name__ == "__main__":
    main()

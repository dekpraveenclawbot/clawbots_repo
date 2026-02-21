#!/usr/bin/env python3
import os
import base64
from email.utils import parsedate_to_datetime
from datetime import timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDS_FILE = "credentials.json"
TOKEN_FILE = "token.json"
MAX_RESULTS = int(os.getenv("MAX_EMAILS", "10"))


def decode_body(payload):
    if not payload:
        return ""

    # Prefer text/plain
    parts = payload.get("parts", [])
    if parts:
        for part in parts:
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        # fallback: recurse once
        for part in parts:
            nested = decode_body(part)
            if nested:
                return nested

    data = payload.get("body", {}).get("data")
    if data:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    return ""


def header(headers, name, default=""):
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", default)
    return default


def summarize(text, max_len=300):
    clean = " ".join((text or "").split())
    if not clean:
        return "(no plain-text body)"
    return clean[:max_len] + ("…" if len(clean) > max_len else "")


def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDS_FILE):
                raise SystemExit(
                    "Missing credentials.json. See EMAIL_OAUTH_SETUP.md to create it from Google Cloud."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def main():
    service = get_service()

    resp = (
        service.users()
        .messages()
        .list(userId="me", q="is:unread", maxResults=MAX_RESULTS)
        .execute()
    )
    msgs = resp.get("messages", [])

    if not msgs:
        print("No unread emails ✅")
        return

    print(f"Unread emails found: {len(msgs)} (showing up to {MAX_RESULTS})")

    for i, m in enumerate(msgs, start=1):
        detail = (
            service.users()
            .messages()
            .get(userId="me", id=m["id"], format="full")
            .execute()
        )

        headers = detail.get("payload", {}).get("headers", [])
        subject = header(headers, "Subject", "(no subject)")
        sender = header(headers, "From", "(unknown sender)")
        date_raw = header(headers, "Date", "")

        try:
            dt = parsedate_to_datetime(date_raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            date_fmt = dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        except Exception:
            date_fmt = date_raw

        body = decode_body(detail.get("payload", {}))

        print(f"\n{i}. {subject}")
        print(f"   From: {sender}")
        print(f"   Date: {date_fmt}")
        print(f"   Preview: {summarize(body)}")


if __name__ == "__main__":
    main()

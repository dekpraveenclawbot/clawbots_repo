# Google Calendar API Setup (Direct Event Creation)

This lets Dek create events directly in your Google Calendar.

## 1) Reuse your existing `credentials.json`

If you already created OAuth Desktop credentials for Gmail API, the same `credentials.json` works.

If not, create one in Google Cloud Console:
1. Open https://console.cloud.google.com/
2. Select project
3. Enable **Google Calendar API**
4. OAuth consent screen (External is fine for personal use)
5. Create OAuth Client ID → **Desktop app**
6. Download JSON to workspace root as `credentials.json`

## 2) Install dependencies

```bash
python3 -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## 3) Create an event

```bash
python3 google_calendar_create_event.py \
  --title "Doctor appointment" \
  --start "2026-03-18 08:30" \
  --duration-min 60 \
  --timezone "UTC" \
  --reminder-days "7,1"
```

On first run, Google login/consent opens in browser.

## Notes

- Token is stored in `calendar_token.json`
- Keep `credentials.json` and token files private
- Reminders are popup reminders in Google Calendar

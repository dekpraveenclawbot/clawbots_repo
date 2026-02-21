# Gmail OAuth Setup (Modern + Recommended)

This replaces app passwords with OAuth.

## 1) Create Google Cloud OAuth credentials

1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create/select a project.
3. Enable **Gmail API**.
4. Configure OAuth consent screen (External is fine for personal use).
5. Create OAuth client credentials:
   - Type: **Desktop app**
6. Download the JSON and save it as:
   - `credentials.json` in this workspace root.

## 2) Install dependencies

```bash
python3 -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## 3) Run reader

```bash
python3 gmail_oauth_reader.py
```

First run opens a browser for Google login + consent.

After approval:
- `token.json` is created automatically (cached auth token).
- next runs are non-interactive unless token expires/revoked.

## 4) Optional config

Set max unread emails to show:

```bash
export MAX_EMAILS=10
python3 gmail_oauth_reader.py
```

## Security notes

- Keep `credentials.json` and `token.json` private.
- Revoke access anytime from: https://myaccount.google.com/permissions

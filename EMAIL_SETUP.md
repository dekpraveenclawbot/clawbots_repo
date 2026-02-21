# Gmail Reader Setup

## 1) Create `.env`

Copy `.env.example` to `.env` and fill in your Gmail + app password:

```bash
cp .env.example .env
```

Then edit `.env`:

```env
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_SECURE=true
IMAP_USER=your_email@gmail.com
IMAP_PASS=your_16_char_app_password
MAILBOX=INBOX
MAX_EMAILS=10
```

## 2) Run

```bash
python3 gmail_reader.py
```

This will list unread emails with sender, date, and a short preview.

## Security Notes

- Use a Gmail **App Password**, not your normal password.
- Keep `.env` private.
- If needed, revoke the app password anytime in Google account security settings.

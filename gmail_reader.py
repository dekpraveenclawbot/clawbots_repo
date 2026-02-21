#!/usr/bin/env python3
import os
import imaplib
import email
from email.header import decode_header
from datetime import datetime


def load_env(path='.env'):
    env = {}
    if not os.path.exists(path):
        return env
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def env_get(name, default=None):
    return os.environ.get(name) or ENV.get(name, default)


def decode_mime(value):
    if not value:
        return ''
    parts = decode_header(value)
    out = []
    for text, enc in parts:
        if isinstance(text, bytes):
            out.append(text.decode(enc or 'utf-8', errors='replace'))
        else:
            out.append(text)
    return ''.join(out)


def get_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = (part.get('Content-Disposition') or '').lower()
            if ctype == 'text/plain' and 'attachment' not in disp:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or 'utf-8'
                    return payload.decode(charset, errors='replace').strip()
        return ''
    payload = msg.get_payload(decode=True)
    if not payload:
        return ''
    charset = msg.get_content_charset() or 'utf-8'
    return payload.decode(charset, errors='replace').strip()


def summarize(text, max_len=300):
    if not text:
        return '(no plain-text body)'
    text = ' '.join(text.split())
    return text[:max_len] + ('…' if len(text) > max_len else '')


ENV = load_env()

HOST = env_get('IMAP_HOST', 'imap.gmail.com')
PORT = int(env_get('IMAP_PORT', '993'))
SECURE = env_get('IMAP_SECURE', 'true').lower() == 'true'
USER = env_get('IMAP_USER')
PASS = env_get('IMAP_PASS')
MAILBOX = env_get('MAILBOX', 'INBOX')
MAX_EMAILS = int(env_get('MAX_EMAILS', '10'))

if not USER or not PASS:
    raise SystemExit('Missing IMAP_USER or IMAP_PASS. Add them to .env (see .env.example).')

conn = None
try:
    conn = imaplib.IMAP4_SSL(HOST, PORT) if SECURE else imaplib.IMAP4(HOST, PORT)
    conn.login(USER, PASS)
    conn.select(MAILBOX)

    status, data = conn.search(None, 'UNSEEN')
    if status != 'OK':
        raise SystemExit('Failed to search mailbox for UNSEEN messages.')

    ids = data[0].split()
    if not ids:
        print('No unread emails ✅')
        raise SystemExit(0)

    print(f'Unread emails: {len(ids)} (showing up to {MAX_EMAILS})')
    to_show = ids[-MAX_EMAILS:][::-1]

    for idx, msg_id in enumerate(to_show, start=1):
        status, msg_data = conn.fetch(msg_id, '(RFC822)')
        if status != 'OK':
            print(f'\n{idx}. [Failed to fetch message {msg_id.decode()}]')
            continue

        raw = None
        for part in msg_data:
            if isinstance(part, tuple):
                raw = part[1]
                break
        if not raw:
            continue

        msg = email.message_from_bytes(raw)
        subject = decode_mime(msg.get('Subject', '(no subject)'))
        sender = decode_mime(msg.get('From', '(unknown sender)'))
        date_raw = msg.get('Date', '')
        body = summarize(get_body(msg))

        print(f'\n{idx}. {subject}')
        print(f'   From: {sender}')
        print(f'   Date: {date_raw}')
        print(f'   Preview: {body}')

finally:
    if conn is not None:
        try:
            conn.close()
        except Exception:
            pass
        try:
            conn.logout()
        except Exception:
            pass

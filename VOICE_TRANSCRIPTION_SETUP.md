# Voice Transcription Setup

Transcription is now available locally with `faster-whisper` in `.venv`.

## Usage

```bash
cd /home/praveen/.openclaw/workspace
. .venv/bin/activate
python transcribe_voice.py /path/to/audio.ogg --model tiny
```

## Notes

- Works with `.ogg`, `.mp3`, `.wav`, `.m4a`
- Start with `--model tiny` (fast)
- For better accuracy, try `--model base` or `--model small`
- You can force language, e.g. `--language en`

## Example (this chat's sample)

```bash
python transcribe_voice.py /home/praveen/.openclaw/media/inbound/file_6---ce290a3b-24b9-4b43-94d1-36a042b7635f.ogg --model tiny
```

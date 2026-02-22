#!/usr/bin/env python3
import argparse
import os
import time
from pathlib import Path

from faster_whisper import WhisperModel

AUDIO_EXTS = {".ogg", ".mp3", ".wav", ".m4a", ".aac", ".flac"}


def cleanup_old_audio(folder: str, keep_days: int = 1):
    p = Path(folder)
    if not p.exists() or not p.is_dir():
        return 0

    cutoff = time.time() - (keep_days * 24 * 60 * 60)
    deleted = 0

    for f in p.iterdir():
        if not f.is_file():
            continue
        if f.suffix.lower() not in AUDIO_EXTS:
            continue
        try:
            if f.stat().st_mtime < cutoff:
                f.unlink()
                deleted += 1
        except Exception:
            pass

    return deleted


def main():
    p = argparse.ArgumentParser(description="Transcribe an audio file with faster-whisper")
    p.add_argument("audio", help="Path to audio file (ogg/mp3/wav/m4a)")
    p.add_argument("--model", default="tiny", help="Model size: tiny, base, small, medium, large-v3")
    p.add_argument("--language", default=None, help="Language code like en, hi; omit for auto-detect")
    p.add_argument("--task", default="transcribe", choices=["transcribe", "translate"])
    p.add_argument(
        "--cleanup-folder",
        default="/home/praveen/.openclaw/media/inbound",
        help="Folder to clean old audio files from (default: OpenClaw inbound media)",
    )
    p.add_argument(
        "--keep-days",
        type=int,
        default=1,
        help="Keep audio files for this many days before cleanup (default: 1)",
    )
    p.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Disable automatic cleanup run",
    )
    args = p.parse_args()

    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(args.audio, language=args.language, task=args.task, vad_filter=True)

    print(f"Detected language: {info.language} (p={info.language_probability:.2f})")
    print("---")
    for seg in segments:
        print(seg.text.strip())

    if not args.no_cleanup:
        deleted = cleanup_old_audio(args.cleanup_folder, args.keep_days)
        print(f"---\nCleanup: deleted {deleted} old audio file(s) from {args.cleanup_folder}")


if __name__ == "__main__":
    main()

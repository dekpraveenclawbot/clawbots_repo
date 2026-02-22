#!/usr/bin/env python3
import argparse
from faster_whisper import WhisperModel


def main():
    p = argparse.ArgumentParser(description="Transcribe an audio file with faster-whisper")
    p.add_argument("audio", help="Path to audio file (ogg/mp3/wav/m4a)")
    p.add_argument("--model", default="tiny", help="Model size: tiny, base, small, medium, large-v3")
    p.add_argument("--language", default=None, help="Language code like en, hi; omit for auto-detect")
    p.add_argument("--task", default="transcribe", choices=["transcribe", "translate"])
    args = p.parse_args()

    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(args.audio, language=args.language, task=args.task, vad_filter=True)

    print(f"Detected language: {info.language} (p={info.language_probability:.2f})")
    print("---")
    for seg in segments:
        print(seg.text.strip())


if __name__ == "__main__":
    main()

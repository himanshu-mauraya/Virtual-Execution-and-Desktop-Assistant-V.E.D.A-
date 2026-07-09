"""Test script to start Vosk recognizer and print transcriptions.
Run with the project's venv to use the same environment.
"""
import time
from veda_ai.bootstrap import load_app_config, build_app_context

if __name__ == "__main__":
    config = load_app_config()
    ctx = build_app_context(config)
    recognizer = ctx.recognizer
    if recognizer is None:
        print("No recognizer available in context.")
        raise SystemExit(1)

    print("Recognizer available:", type(recognizer).__name__)
    try:
        recognizer.start_listening()
    except Exception as exc:
        print("Failed to start recognizer:", exc)
        raise

    print("Listening for 20 seconds. Speak into your microphone...")
    start = time.time()
    try:
        while time.time() - start < 20:
            text = recognizer.get_transcription()
            if text:
                print("TRANSCRIPTION:", text)
            time.sleep(0.3)
    finally:
        recognizer.stop_listening()
        print("Stopped listening.")

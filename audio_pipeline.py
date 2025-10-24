"""
audio_pipeline.py
Final homework pipeline for audio transcription and summary.
All files are in the same folder (Lab3).
"""

import os
import logging
from io import BytesIO
from pydub import AudioSegment
import speech_recognition as sr

# Optional TTS
try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# ----------------------------
# ----------------------------
# CONFIG
# ----------------------------
INPUT_AUDIO = "test_audio.m4a"          # Change to your m4a file
TRANSCRIPT_FILE = "output_transcript.txt"
SUMMARY_FILE = "output_summary.mp3"
LOG_FILE = "audit.log"
CHUNK_MS = 10000                         # 10-second chunks

# ----------------------------
# SETUP LOGGING
# ----------------------------
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)

# ----------------------------
# LOAD AUDIO
# ----------------------------
try:
    ext = os.path.splitext(INPUT_AUDIO)[1].lower()
    if ext not in [".mp3", ".m4a"]:
        raise ValueError("Unsupported audio format")
    audio = AudioSegment.from_file(INPUT_AUDIO, format=ext.replace(".", ""))
    audio = audio.normalize()  # normalize volume
    logging.info(f"Loaded {INPUT_AUDIO} successfully, duration {len(audio)} ms")
except Exception as e:
    logging.error(f"Failed to load audio: {e}")
    raise SystemExit(f"Error loading audio: {e}")

# ----------------------------
# INITIALIZE RECOGNIZER
# ----------------------------
recognizer = sr.Recognizer()
transcriptions = []

# ----------------------------
# PROCESS AUDIO IN CHUNKS
# ----------------------------
for i, start_ms in enumerate(range(0, len(audio), CHUNK_MS)):
    chunk = audio[start_ms:start_ms + CHUNK_MS]
    wav_io = BytesIO()
    chunk.export(wav_io, format="wav")
    wav_io.seek(0)

    try:
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        transcriptions.append(text)
        logging.info(f"Chunk {i+1} transcribed successfully")
        print(f"✅ Chunk {i+1}: {text}")
    except sr.UnknownValueError:
        logging.warning(f"Chunk {i+1} could not be understood")
        print(f"❌ Chunk {i+1}: Could not understand")
    except sr.RequestError as e:
        logging.error(f"Chunk {i+1} API error: {e}")
        print(f"⚠️ Chunk {i+1} API error: {e}")

# ----------------------------
# SAVE TRANSCRIPT
# ----------------------------
try:
    with open(TRANSCRIPT_FILE, "w", encoding="utf-8") as f:
        for i, text in enumerate(transcriptions):
            f.write(f"Chunk {i+1}: {text}\n")
    logging.info(f"Transcript saved to {TRANSCRIPT_FILE}")
except Exception as e:
    logging.error(f"Failed to save transcript: {e}")

# ----------------------------
# GENERATE AUDIO SUMMARY (OPTIONAL)
# ----------------------------
if TTS_AVAILABLE and transcriptions:
    summary_text = " ".join(transcriptions[:3])  # simple summary using first 3 chunks
    try:
        tts = gTTS(summary_text)
        tts.save(SUMMARY_FILE)
        logging.info(f"Audio summary saved to {SUMMARY_FILE}")
        print(f"✅ Audio summary saved to {SUMMARY_FILE}")
    except Exception as e:
        logging.error(f"Failed to generate audio summary: {e}")
        print(f"❌ Failed to generate audio summary: {e}")
elif not TTS_AVAILABLE:
    logging.warning("gTTS not installed; skipping audio summary")
    print("⚠️ gTTS not installed; skipping audio summary")

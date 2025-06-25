import whisper
import requests
import json
import argparse
import os
import sys
from datetime import datetime

# === SMS CONFIG ===
API_URL = "https://your-api-endpoint.com/send"  # Replace with your endpoint
API_TOKEN = "your_api_token_here"
CONTACTS = ["2547XXXXXXXX", "2547YYYYYYYY"]  # Replace with real phone numbers
SENDER_ID = "LIFEWAY"

# === Parse CLI arguments ===
parser = argparse.ArgumentParser(description="Transcribe audio and send SMS summary.")
parser.add_argument("--audio", required=True, help="Path to the audio file")
parser.add_argument("--model", default="large-v2", help="Whisper model to use (tiny, base, small, medium, large, large-v2)")
parser.add_argument("--language", default=None, help="Language code (e.g., 'en' for English)")
args = parser.parse_args()

audio_path = args.audio
model_size = args.model
language = args.language

# === Validate file ===
if not os.path.exists(audio_path):
    print(f"[!] Audio file not found: {audio_path}")
    sys.exit(1)

# Get file size for info
file_size = os.path.getsize(audio_path) / (1024 * 1024)  # MB
print(f"[*] Audio file size: {file_size:.2f} MB")

# === Transcribe with improved settings ===
print(f"[*] Loading Whisper model: {model_size}")
model = whisper.load_model(model_size)

print(f"[*] Transcribing: {audio_path}")
print("[*] This may take a while for long audio files...")

# Improved transcription with better parameters
transcribe_options = {
    "verbose": True,  # Show progress
    "temperature": 0.0,  # More deterministic
    "compression_ratio_threshold": 2.4,  # Detect low-quality audio
    "logprob_threshold": -1.0,  # Filter out low-confidence segments
    "no_speech_threshold": 0.6,  # Better silence detection
    "condition_on_previous_text": False,  # Reduce repetition
}

# Add language if specified
if language:
    transcribe_options["language"] = language

try:
    result = model.transcribe(audio_path, **transcribe_options)
    transcribed_text = result["text"]
    
    # Check if transcription seems problematic
    if len(transcribed_text.strip()) < 50:
        print("[!] WARNING: Transcription is very short. This might indicate audio quality issues.")
    
    # Check for excessive repetition (dots, repeated phrases)
    dot_ratio = transcribed_text.count('.') / len(transcribed_text) if transcribed_text else 0
    if dot_ratio > 0.1:
        print("[!] WARNING: High number of dots detected. This often indicates audio quality issues.")
    
    print("[+] Transcription complete.")
    print(f"[*] Transcription length: {len(transcribed_text)} characters")
    print(f"[*] First 200 characters: {transcribed_text[:200]}...")
    
except Exception as e:
    print(f"[!] Transcription failed: {str(e)}")
    sys.exit(1)

# === Save to .txt file ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
basename = os.path.splitext(os.path.basename(audio_path))[0]
output_filename = f"{basename}_transcript_{timestamp}.txt"

with open(output_filename, "w", encoding="utf-8") as f:
    f.write(f"Transcription of: {audio_path}\n")
    f.write(f"Model used: {model_size}\n")
    f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"File size: {file_size:.2f} MB\n")
    f.write("=" * 50 + "\n\n")
    f.write(transcribed_text)

print(f"[+] Transcript saved to: {output_filename}")

# === Send SMS ===
def send_sms(contact, message):
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "senderID": SENDER_ID,
        "message": message,
        "phones": contact
    }
    print(f"[*] Sending SMS to {contact}...")
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print(f"[+] SMS sent to {contact}.")
        else:
            print(f"[!] Failed to send SMS to {contact}: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"[!] SMS sending failed: {str(e)}")

# === Send to each contact ===
# Truncate message to avoid SMS length limits
preview_text = transcribed_text[:100] if len(transcribed_text) > 100 else transcribed_text
summary_msg = f"Transcription complete. File: {output_filename}\nLength: {len(transcribed_text)} chars\nPreview: {preview_text}..."

for number in CONTACTS:
    send_sms(number, summary_msg)

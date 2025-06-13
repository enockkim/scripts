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
args = parser.parse_args()
audio_path = args.audio

# === Validate file ===
if not os.path.exists(audio_path):
    print(f"[!] Audio file not found: {audio_path}")
    sys.exit(1)

# === Transcribe === Use medium
print("[*] Loading Whisper model...")
model = whisper.load_model("medium") 

print(f"[*] Transcribing: {audio_path}")
result = model.transcribe(audio_path)
transcribed_text = result["text"]
print("[+] Transcription complete.")
print(transcribed_text)

# === Save to .txt file ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
basename = os.path.splitext(os.path.basename(audio_path))[0]
output_filename = f"{basename}_transcript_{timestamp}.txt"

with open(output_filename, "w", encoding="utf-8") as f:
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
    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print(f"[+] SMS sent to {contact}.")
    else:
        print(f"[!] Failed to send SMS to {contact}: {response.status_code}")
        print(response.text)

# === Send to each contact ===
summary_msg = f"Transcription complete. File: {output_filename}\nPreview: {transcribed_text[:100]}"
for number in CONTACTS:
    send_sms(number, summary_msg)

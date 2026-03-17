from flask import Flask, request, jsonify
import imaplib
import email
import time
import threading
import os

app = Flask(__name__)

GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_PASS = os.environ.get("GMAIL_PASS", "")

def process_alert(raw_message):
    # Decode encoded email subjects
    from email.header import decode_header
    decoded_parts = decode_header(raw_message)
    message = ""
    for part, enc in decoded_parts:
        if isinstance(part, bytes):
            message += part.decode(enc or "utf-8")
        else:
            message += str(part)

    message = message.upper()
    print(f"ALERT: {message}")

    action = None
    price  = None

    if "ENTRY" in message:
        action = "ENTRY"
        if "AT" in message:
            try:
                price = float(message.split("AT")[-1].strip().split()[0])
            except:
                price = None
    elif "TARGET HIT" in message:
        action = "TARGET"
    elif "SL HIT" in message:
        action = "SL"

    print(f"Action: {action} | Price: {price}")

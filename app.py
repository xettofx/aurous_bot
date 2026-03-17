from flask import Flask, request, jsonify
from email.header import decode_header
import imaplib
import email
import time
import threading
import os

app = Flask(__name__)

GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_PASS = os.environ.get("GMAIL_PASS", "")

def process_alert(raw_message):
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
    # TODO: broker execution goes here in Step 4

def check_email():
    while True:
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(GMAIL_USER, GMAIL_PASS)
            mail.select("inbox")
            _, msgs = mail.search(None, "(UNSEEN)")
            for num in msgs[0].split():
                _, data = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])
                subject = msg["subject"] or ""
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()
                full_text = subject + " " + body
                process_alert(full_text)
                mail.store(num, "+FLAGS", "\\Seen")
            mail.logout()
        except Exception as e:
            print(f"Email error: {e}")
        time.sleep(10)

# Start email thread when module loads (works with gunicorn)
email_thread = threading.Thread(target=check_email, daemon=True)
email_thread.start()

@app.route("/")
def index():
    return "Aurous Bot is live.", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

from flask import Flask, request, jsonify
import os

app = Flask(__name__)

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "aurous123")

@app.route("/webhook", methods=["POST"])
def webhook():
    token = request.args.get("token", "")
    if token != WEBHOOK_SECRET:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    message = request.data.decode("utf-8")

    print(f"ALERT RECEIVED: {message}")

    # Parse the alert
    action   = None
    ticker   = None
    price    = None

    if "ENTRY" in message:
        if "XAUUSD" in message or "GOLD" in message:
            ticker = "XAUUSD"
        action = "ENTRY"
        # Extract price after "at"
        if "at" in message:
            try:
                price = float(message.split("at")[-1].strip())
            except:
                price = None

    elif "TARGET HIT" in message:
        action = "TARGET"
    elif "SL HIT" in message:
        action = "SL"

    print(f"Action: {action} | Ticker: {ticker} | Price: {price}")

    # TODO: broker execution goes here in Step 3
    return jsonify({"status": "received", "action": action, "price": price}), 200

@app.route("/")
def index():
    return "Aurous Bot is live.", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

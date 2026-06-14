"""
test_webhook.py
---------------
Runs a local Flask server that mimics the webhook endpoints Retell AI
will call during and after conversations. Use this for local testing
before deploying your backend.

Logs all incoming webhook payloads to the console in readable format.
Optionally validates that required fields are present.

Usage:
    pip install flask python-dotenv
    python scripts/test_webhook.py

Then run ngrok to expose locally:
    ngrok http 5001

Paste the ngrok URL into your Retell agent webhook config for testing.

Retell webhook events this server handles:
    POST /webhooks/call-started     — fires when a call connects
    POST /webhooks/call-ended       — fires when the call ends (includes transcript)
    POST /webhooks/slot-filled      — fires when agent fills a data slot
    POST /webhooks/appointment-confirmed — fires when agent confirms a booking
"""

import json
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)


def log_event(event_name: str, payload: dict):
    """Pretty-print an incoming webhook payload."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n{'='*60}")
    print(f"[{timestamp}] EVENT: {event_name}")
    print(f"{'='*60}")
    print(json.dumps(payload, indent=2))
    print()


@app.route("/webhooks/call-started", methods=["POST"])
def call_started():
    """
    Fires when an inbound call connects to the agent.
    Payload includes: call_id, from_number, to_number, start_time
    """
    payload = request.get_json(silent=True) or {}
    log_event("CALL STARTED", payload)

    call_id = payload.get("call_id", "unknown")
    from_number = payload.get("from_number", "unknown")

    print(f"  > Call ID:   {call_id}")
    print(f"  > From:      {from_number}")

    return jsonify({"status": "received", "call_id": call_id}), 200


@app.route("/webhooks/call-ended", methods=["POST"])
def call_ended():
    """
    Fires when the call ends.
    Payload includes: call_id, duration_seconds, transcript, collected_data, end_reason
    """
    payload = request.get_json(silent=True) or {}
    log_event("CALL ENDED", payload)

    call_id = payload.get("call_id", "unknown")
    duration = payload.get("duration_seconds", 0)
    end_reason = payload.get("end_reason", "unknown")
    transcript = payload.get("transcript", [])

    print(f"  > Call ID:    {call_id}")
    print(f"  > Duration:   {duration}s")
    print(f"  > End reason: {end_reason}")

    if transcript:
        print(f"\n  TRANSCRIPT ({len(transcript)} turns):")
        for turn in transcript:
            role = turn.get("role", "?").upper()
            content = turn.get("content", "")
            print(f"    [{role}] {content}")

    collected = payload.get("collected_data", {})
    if collected:
        print(f"\n  COLLECTED DATA:")
        for key, val in collected.items():
            print(f"    {key}: {val}")

    return jsonify({"status": "received"}), 200


@app.route("/webhooks/slot-filled", methods=["POST"])
def slot_filled():
    """
    Fires each time the agent successfully fills a required data slot.
    Payload includes: call_id, slot_name, slot_value, all_slots_filled
    """
    payload = request.get_json(silent=True) or {}
    log_event("SLOT FILLED", payload)

    slot_name = payload.get("slot_name", "unknown")
    slot_value = payload.get("slot_value", "unknown")
    all_filled = payload.get("all_slots_filled", False)

    print(f"  > Slot:       {slot_name} = {slot_value}")
    print(f"  > All filled: {all_filled}")

    if all_filled:
        print("  > [TRIGGER] All required slots filled. Ready to write to Open Dental.")

    return jsonify({"status": "received"}), 200


@app.route("/webhooks/appointment-confirmed", methods=["POST"])
def appointment_confirmed():
    """
    Fires when the agent reads back appointment details and caller confirms.
    This is the trigger to write to Open Dental.

    Required fields: patient_first_name, patient_last_name, date_of_birth,
                     appointment_reason, appointment_datetime
    """
    payload = request.get_json(silent=True) or {}
    log_event("APPOINTMENT CONFIRMED", payload)

    required_fields = [
        "patient_first_name",
        "patient_last_name",
        "date_of_birth",
        "appointment_reason",
        "appointment_datetime"
    ]

    missing = [f for f in required_fields if not payload.get(f)]

    if missing:
        print(f"  > [WARNING] Missing required fields: {missing}")
        print("  > Would not write to Open Dental without these fields.")
        return jsonify({"status": "error", "missing_fields": missing}), 422

    print(f"\n  APPOINTMENT DETAILS:")
    print(f"    Patient:   {payload['patient_first_name']} {payload['patient_last_name']}")
    print(f"    DOB:       {payload['date_of_birth']}")
    print(f"    Reason:    {payload['appointment_reason']}")
    print(f"    DateTime:  {payload['appointment_datetime']}")
    print(f"\n  > [TRIGGER] Writing appointment to Open Dental...")
    print("  > (In production, Open Dental API POST /appointments would fire here)")

    return jsonify({
        "status": "received",
        "action": "open_dental_write_triggered",
        "patient": f"{payload['patient_first_name']} {payload['patient_last_name']}"
    }), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "server": "ZNX AI webhook test server"}), 200


if __name__ == "__main__":
    print("\nZNX AI Local Webhook Test Server")
    print("="*40)
    print("Listening on http://localhost:5001")
    print("Endpoints:")
    print("  POST /webhooks/call-started")
    print("  POST /webhooks/call-ended")
    print("  POST /webhooks/slot-filled")
    print("  POST /webhooks/appointment-confirmed")
    print("  GET  /health")
    print("\nExpose with ngrok: ngrok http 5001")
    print("="*40 + "\n")
    app.run(host="0.0.0.0", port=5001, debug=True)

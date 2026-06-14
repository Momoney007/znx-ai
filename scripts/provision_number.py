"""
provision_number.py
-------------------
Provisions a local Twilio phone number for a dental practice and configures
it to route inbound calls to a Retell AI agent webhook.

Usage:
    python scripts/provision_number.py --area-code 713 --practice "Houston Family Dental"

Requirements:
    pip install twilio python-dotenv

Environment variables (set in .env file, never commit .env to git):
    TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
    TWILIO_AUTH_TOKEN=your_auth_token
    RETELL_INBOUND_WEBHOOK=https://api.retellai.com/twilio-streams/[YOUR_AGENT_ID]
"""

import os
import argparse
from dotenv import load_dotenv

load_dotenv()

try:
    from twilio.rest import Client
except ImportError:
    raise ImportError("Run: pip install twilio python-dotenv")


def provision_number(area_code: str, practice_name: str, dry_run: bool = False):
    """
    Search for an available local number in the given area code and provision it.
    Configures the number to route voice calls to the Retell AI agent webhook.
    """
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    retell_webhook = os.environ.get("RETELL_INBOUND_WEBHOOK")

    if not all([account_sid, auth_token, retell_webhook]):
        raise EnvironmentError(
            "Missing required environment variables. "
            "Check that TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and "
            "RETELL_INBOUND_WEBHOOK are set in your .env file."
        )

    client = Client(account_sid, auth_token)

    print(f"\nSearching for available numbers in area code {area_code}...")
    available = client.available_phone_numbers("US").local.list(
        area_code=area_code,
        limit=5
    )

    if not available:
        print(f"No available numbers found for area code {area_code}.")
        print("Try a nearby area code or use Twilio console to search broader regions.")
        return None

    print(f"\nFound {len(available)} available numbers:")
    for i, num in enumerate(available):
        print(f"  [{i}] {num.phone_number} — {num.friendly_name}")

    selected = available[0]
    print(f"\nSelecting: {selected.phone_number}")

    if dry_run:
        print("\n[DRY RUN] Number not actually provisioned. Remove --dry-run to provision.")
        return selected.phone_number

    print("\nProvisioning number and configuring webhook...")
    purchased = client.incoming_phone_numbers.create(
        phone_number=selected.phone_number,
        friendly_name=f"ZNX AI — {practice_name}",
        voice_url=retell_webhook,
        voice_method="POST",
        status_callback=os.environ.get("STATUS_CALLBACK_URL", ""),
        status_callback_method="POST"
    )

    print(f"\nSuccess.")
    print(f"  SID:     {purchased.sid}")
    print(f"  Number:  {purchased.phone_number}")
    print(f"  Label:   {purchased.friendly_name}")
    print(f"  Webhook: {purchased.voice_url}")
    print(f"\nThis number is now live. Calls will route to your Retell agent.")
    print(f"Log into Twilio console to verify: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming")

    return purchased.phone_number


def list_provisioned_numbers():
    """List all phone numbers currently provisioned on the Twilio account."""
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    client = Client(account_sid, auth_token)

    numbers = client.incoming_phone_numbers.list()
    if not numbers:
        print("No numbers currently provisioned on this account.")
        return

    print(f"\nProvisioned numbers ({len(numbers)}):")
    for num in numbers:
        print(f"  {num.phone_number} — {num.friendly_name} — Voice: {num.voice_url}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Provision a Twilio number for ZNX AI")
    parser.add_argument("--area-code", type=str, default="713", help="US area code to search (default: 713)")
    parser.add_argument("--practice", type=str, required=True, help="Practice name for number label")
    parser.add_argument("--dry-run", action="store_true", help="Search without purchasing")
    parser.add_argument("--list", action="store_true", help="List currently provisioned numbers")
    args = parser.parse_args()

    if args.list:
        list_provisioned_numbers()
    else:
        provision_number(
            area_code=args.area_code,
            practice_name=args.practice,
            dry_run=args.dry_run
        )

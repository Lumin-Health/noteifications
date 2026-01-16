import logging
import os
from hubspot_client import HubSpotClient
from config import WORKFLOW_WEBHOOK_URL_EPISODE

# Config updated in config.py
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_test():
    # Real Data from User/HubSpot
    TARGET_OBJECT_ID = "45288451901"
    TARGET_OBJECT_TYPE = "2-54812380" # Treatment Episode
    NOTE_ID = "101386699330"
    AUTHOR_USER_ID = "77395606"
    
    # Override URL for this test
    TEST_WEBHOOK_URL = "https://api-na1.hubapi.com/automation/v4/webhook-triggers/50831618/n3bB66h"

    print(f"Triggering Workflow Webhook: {TEST_WEBHOOK_URL}")
    print(f"Target: Object={TARGET_OBJECT_ID}, Note={NOTE_ID}, Author={AUTHOR_USER_ID}")

    client = HubSpotClient()
    
    # 1. Fetch Dynamic Object Name
    object_name = client.get_object_name(TARGET_OBJECT_TYPE, TARGET_OBJECT_ID)
    print(f"Resolved Object Name: {object_name}")

    # 2. Fetch Dynamic Author Name
    author_name = "Unknown Author"
    author_details = client.get_owner_details(AUTHOR_USER_ID)
    if author_details:
        fn = getattr(author_details, "first_name", "") or ""
        ln = getattr(author_details, "last_name", "") or ""
        full_name = f"{fn} {ln}".strip()
        if full_name:
            author_name = full_name
        elif getattr(author_details, "email", None):
            author_name = author_details.email
    print(f"Resolved Author Name: {author_name}")

    # 3. Payload Construction
    # Workflow expects lowercase keys: authorname, objectname, objecttypename
    trigger_payload = {
        "objectId": TARGET_OBJECT_ID,
        "objectType": TARGET_OBJECT_TYPE,
        "objectname": object_name,
        "objecttypename": "Treatment Episode",
        "noteId": NOTE_ID,
        "authorUserId": AUTHOR_USER_ID,
        "authorname": author_name
    }

    try:
        response = client.trigger_workflow_via_webhook(TEST_WEBHOOK_URL, trigger_payload)
        print("Success! Response:", response)
    except Exception as e:
        print("Failed to trigger webhook:", e)

if __name__ == "__main__":
    # Ensure env var is set if not in config defaults (it is in config.py now, but let's be safe)
    run_test()

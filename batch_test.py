from hubspot_client import HubSpotClient
import logging

logging.basicConfig(level=logging.INFO)

def run_batch_tests():
    client = HubSpotClient()
    
    # Test Case 1: Insurance Authorization
    print("--- Running Test Case 1: Insurance Authorization ---")
    AUTH_OBJECT_ID = "44816808554"
    AUTH_NOTE_ID = "101380571553"
    AUTH_AUTHOR_ID = "77395606"
    AUTH_WEBHOOK_URL = "https://api-na1.hubapi.com/automation/v4/webhook-triggers/50831618/j6EloSG"
    
    # Fetch names dynamically to emulate real flow
    object_name = client.get_object_name("2-54811911", AUTH_OBJECT_ID)
    author_details = client.get_owner_details(AUTH_AUTHOR_ID)
    author_name = f"{getattr(author_details, 'first_name', '')} {getattr(author_details, 'last_name', '')}".strip() or getattr(author_details, 'email', 'Unknown')
    
    payload_auth = {
        "objectId": AUTH_OBJECT_ID,
        "objectType": "2-54811911",
        "objectname": object_name,
        "objecttypename": "Insurance Authorization",
        "noteId": AUTH_NOTE_ID,
        "authorUserId": AUTH_AUTHOR_ID,
        "authorname": author_name
    }
    
    try:
        print(f"Triggering Auth Webhook: {AUTH_WEBHOOK_URL}")
        resp = client.trigger_workflow_via_webhook(AUTH_WEBHOOK_URL, payload_auth)
        print("Auth Test Result:", resp)
    except Exception as e:
        print("Auth Test Failed:", e)

    print("\n")

    # Test Case 2: Treatment Episode
    print("--- Running Test Case 2: Treatment Episode ---")
    EPISODE_OBJECT_ID = "44933152642"
    EPISODE_NOTE_ID = "101391354421"
    EPISODE_AUTHOR_ID = "77395606"
    EPISODE_WEBHOOK_URL = "https://api-na1.hubapi.com/automation/v4/webhook-triggers/50831618/n3bB66h"
    
    object_name_ep = client.get_object_name("2-54812380", EPISODE_OBJECT_ID)
    
    payload_ep = {
        "objectId": EPISODE_OBJECT_ID,
        "objectType": "2-54812380",
        "objectname": object_name_ep,
        "objecttypename": "Treatment Episode",
        "noteId": EPISODE_NOTE_ID,
        "authorUserId": EPISODE_AUTHOR_ID,
        "authorname": author_name # Same author
    }
    
    try:
        print(f"Triggering Episode Webhook: {EPISODE_WEBHOOK_URL}")
        resp = client.trigger_workflow_via_webhook(EPISODE_WEBHOOK_URL, payload_ep)
        print("Episode Test Result:", resp)
    except Exception as e:
        print("Episode Test Failed:", e)

if __name__ == "__main__":
    run_batch_tests()

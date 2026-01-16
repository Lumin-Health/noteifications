import logging
import functions_framework
from flask import jsonify
from hubspot_client import HubSpotClient
from config import WORKFLOW_WEBHOOK_URL_AUTH # Optional generic import if needed, but we import dynamically now

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def handle_webhook(request):
    """
    Entry point for the Cloud Function.
    Handles 'Note Created' webhooks from HubSpot.
    """
    try:
        # 1. Parse Request
        if request.method != 'POST':
            return "Method Not Allowed", 405

        payload = request.get_json(silent=True)
        if not payload:
            return "Bad Request: No JSON payload", 400

        logger.info(f"Received payload: {len(payload)} events")

        # HubSpot webhooks often send a list of events
        # We process each event.
        client = HubSpotClient()
        
        results = []

        for event in payload:
            object_id = event.get('objectId')
            
            # Note ID is the 'objectId' in the webhook for a note event
            note_id = object_id
            
            if not note_id:
                logger.warning(f"Skipping event {event.get('eventId')}: No objectId (Note ID) found.")
                continue

            logger.info(f"Processing Note ID: {note_id}")

            # 2. Get Note Details (Author & Associated Object)
            try:
                note = client.get_note_details(note_id)
            except Exception as e:
                logger.error(f"Failed to fetch note {note_id}: {e}")
                continue

            properties = note.properties or {}
            author_user_id = properties.get("hs_created_by_user_id")
            
            # Identify Associated Object (Contact or Custom)
            # We look for associations in the note data
            associations = note.associations or {}
            
            # Prioritize standard objects, then custom?
            target_object_id = None
            target_object_type = None
            
            # Check Contacts
            if associations:
                logger.info(f"Available associations keys: {list(associations.keys())}")

            if associations.get("contacts"):
                 target_object_id = associations["contacts"].results[0].id
                 target_object_type = "contacts"
            # Check Treatment Episodes
            # The key is dynamic e.g. 'p50831618_treatment_episodes'
            elif associations.get("p50831618_treatment_episodes"):
                 target_object_id = associations["p50831618_treatment_episodes"].results[0].id
                 target_object_type = "2-54812380"
            elif associations.get("2-54812380"):
                 target_object_id = associations["2-54812380"].results[0].id
                 target_object_type = "2-54812380"
            # Check Insurance Authorizations
            elif associations.get("p50831618_insurance_authorizations"):
                 target_object_id = associations["p50831618_insurance_authorizations"].results[0].id
                 target_object_type = "2-54811911"
            elif associations.get("2-54811911"):
                 target_object_id = associations["2-54811911"].results[0].id
                 target_object_type = "2-54811911"
            
            if not target_object_id:
                logger.warning(f"Note {note_id} has no associated contact/object. Skipping.")
                continue

            # 3. Get Object Owner
            owner_id = client.get_object_owner(target_object_type, target_object_id)
            
            # 4. Compare & Trigger
            # Get Owner's User ID for comparison
            owner_user_id = client.get_owner_user_id(owner_id) if owner_id else None

            logger.info(f"Note {note_id}: Author={author_user_id}, Owner={owner_id} (User={owner_user_id})")

            should_trigger = False
            
            if owner_user_id is None:
                # User Rule #6: "no owner assigned should trigger the workflow anyways"
                should_trigger = True
                logger.info("Triggering: Object has no owner.")
            elif str(author_user_id) != str(owner_user_id):
                should_trigger = True
                logger.info(f"Triggering: Mismatch (Author {author_user_id} != Owner {owner_user_id})")
            else:
                logger.info("No Trigger: Author is Owner.")

            if should_trigger:
                # Select correct Webhook URL
                webhook_url = None
                if target_object_type == "2-54811911": # Insurance Authorization
                    from config import WORKFLOW_WEBHOOK_URL_AUTH
                    webhook_url = WORKFLOW_WEBHOOK_URL_AUTH
                elif target_object_type == "2-54812380": # Treatment Episode
                    from config import WORKFLOW_WEBHOOK_URL_EPISODE
                    webhook_url = WORKFLOW_WEBHOOK_URL_EPISODE
                else:
                    # Fallback for generic contacts etc if needed, or default to Auth? 
                    # For now, only these two have specific workflows.
                    logger.warning(f"No specific workflow URL for type {target_object_type}")
                    # Optionally use one as default
                    from config import WORKFLOW_WEBHOOK_URL_AUTH
                    webhook_url = WORKFLOW_WEBHOOK_URL_AUTH

                if webhook_url:
                    # 5. Get Note Author Name
                    author_name = "Unknown"
                    if author_user_id:
                        author_details = client.get_owner_details(author_user_id)
                        if author_details:
                            # Combine firstName and lastName if available
                            fn = getattr(author_details, "first_name", "") or ""
                            ln = getattr(author_details, "last_name", "") or ""
                            full_name = f"{fn} {ln}".strip()
                            if full_name:
                                author_name = full_name
                            elif getattr(author_details, "email", None):
                                author_name = author_details.email
                    
                    # 6. Get Object Name
                    object_name = client.get_object_name(target_object_type, target_object_id)
                    
                    # 7. Get Object Type Name (Simple mapping logic)
                    object_type_name = target_object_type
                    if target_object_type == "contacts" or target_object_type == "0-1":
                        object_type_name = "Contact"
                    elif target_object_type == "companies" or target_object_type == "0-2":
                        object_type_name = "Company"
                    elif target_object_type == "deals" or target_object_type == "0-3":
                         object_type_name = "Deal"
                    elif target_object_type == "2-54812380":
                         object_type_name = "Treatment Episode"
                    elif target_object_type == "2-54811911":
                         object_type_name = "Insurance Authorization"
                    
                    # Construct payload for the webhook
                    trigger_payload = {
                        "objectId": target_object_id,
                        "objectType": target_object_type,
                        "objectname": object_name,
                        "objecttypename": object_type_name,
                        "noteId": note_id,
                        "authorUserId": author_user_id,
                        "authorname": author_name
                    }
                    
                    client.trigger_workflow_via_webhook(webhook_url, trigger_payload)
                    results.append(f"Triggered workflow for {target_object_type} {target_object_id} (Author: {author_name})")
                else:
                    logger.warning("No Webhook URL configured for this object type.")
                    results.append("Skipped trigger: Missing Webhook URL")

        return jsonify({"status": "success", "processed": len(results), "details": results}), 200

    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        return f"Internal Server Error: {e}", 500

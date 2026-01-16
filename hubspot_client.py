import logging
from hubspot import HubSpot
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from config import get_hubspot_access_token

class HubSpotClient:
    def __init__(self):
        self.access_token = get_hubspot_access_token()
        if not self.access_token:
            raise ValueError("HUBSPOT_ACCESS_TOKEN not found.")
        self.client = HubSpot(access_token=self.access_token)
        
    def get_note_details(self, note_id):
        """
        Fetch note details including the author ID and associated objects.
        """
        try:
            # Using 'hubspot_owner_id' for the note usually represents the assignee, 
            # but 'hs_created_by_user_id' is the actual author.
            properties = ["hs_created_by_user_id", "hubspot_owner_id", "hs_note_body"]
            associations = ["contacts", "companies", "deals", "2-54812380", "2-54811911"] # Add custom object types if known ID
            
            # Using generic object retrieval for Note (object type 'notes' or '0-4')
            response = self.client.crm.objects.notes.basic_api.get_by_id(
                note_id=note_id,
                properties=properties,
                associations=associations
            )
            return response
        except Exception as e:
            logger.error(f"Error fetching note {note_id}: {e}")
            raise e

    def get_object_owner(self, object_type, object_id):
        """
        Fetch the 'hubspot_owner_id' for a given object.
        """
        try:
            properties = ["hubspot_owner_id"]
            response = self.client.crm.objects.basic_api.get_by_id(
                object_type=object_type,
                object_id=object_id,
                properties=properties
            )
            return response.properties.get("hubspot_owner_id")
        except Exception as e:
            logger.error(f"Error fetching owner for {object_type}/{object_id}: {e}")
            raise e

    def get_owner_details(self, owner_id):
        """
        Resolve a HubSpot Owner ID (or User ID) to an Owner object (with name/email).
        """
        if not owner_id:
            return None
        try:
            # The owners API often accepts User ID as Owner ID in many contexts
            response = self.client.crm.owners.owners_api.get_by_id(owner_id=owner_id)
            return response
        except Exception as e:
            logger.error(f"Error fetching owner details {owner_id}: {e}")
            return None

    def get_owner_user_id(self, owner_id):
        """
        Resolve a HubSpot Owner ID to a User ID for comparison.
        """
        if not owner_id:
            return None
        try:
            response = self.client.crm.owners.owners_api.get_by_id(owner_id=owner_id)
            # The owner object typically has 'userId' (integer)
            return str(response.user_id) if response.user_id else None
        except Exception as e:
            logger.error(f"Error fetching owner details {owner_id}: {e}")
            # If we can't find the owner, we can't compare. Return None?
            return None

    def get_object_name(self, object_type, object_id):
        """
        Fetch the display name of the object.
        """
        try:
            # Determine properties to fetch based on type
            # Standard mappings
            props = ["name"] # Default for custom objects/companies
            
            if object_type == "contacts" or object_type == "0-1":
                props = ["firstname", "lastname", "email"]
            elif object_type == "deals" or object_type == "0-3":
                props = ["dealname"]
            elif object_type == "tickets" or object_type == "0-5":
                props = ["subject"]
            
            response = self.client.crm.objects.basic_api.get_by_id(
                object_type=object_type,
                object_id=object_id,
                properties=props
            )
            
            p = response.properties
            if object_type == "contacts" or object_type == "0-1":
                 fn = p.get("firstname") or ""
                 ln = p.get("lastname") or ""
                 return f"{fn} {ln}".strip() or p.get("email") or "Unnamed Contact"
            elif object_type == "deals" or object_type == "0-3":
                return p.get("dealname") or "Unnamed Deal"
            elif object_type == "tickets" or object_type == "0-5":
                return p.get("subject") or "Unnamed Ticket"
            
            return p.get("name") or str(object_id)
            
        except Exception as e:
            logger.error(f"Error fetching name for {object_type}/{object_id}: {e}")
            return "Unknown Object"

    def trigger_workflow_via_webhook(self, webhook_url, payload):
        """
        Triggers a HubSpot workflow via a webhook URL using a POST request.
        """
        import requests
        try:
            logger.info(f"Triggering workflow via webhook: {webhook_url}")
            # Webhook triggers usually require POST
            response = requests.post(webhook_url, json=payload, headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            logger.info(f"Successfully triggered workflow via webhook for {payload.get('objectId')}")
            return response.json()
        except Exception as e:
             logger.error(f"Error triggering workflow via webhook: {e}")
             raise e

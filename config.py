import os
from google.cloud import secretmanager

def get_secret(secret_name, project_id):
    """
    Retrieve a secret from Google Cloud Secret Manager.
    """
    if not secret_name or not project_id:
        print(f"Skipping secret fetch: secret_name={secret_name}, project_id={project_id}")
        return None

    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error fetching secret '{secret_name}': {e}")
        raise e

# Configuration
PROJECT_ID = os.environ.get("GCP_PROJECT", "lumininternal")
HUBSPOT_SECRET_NAME = os.environ.get("HUBSPOT_SECRET_NAME", "hubspot-new-standard-sandbox-token")
# Default URLs (can be overridden by environment variables)
# Auth Workflow (2-54811911)
WORKFLOW_WEBHOOK_URL_AUTH = os.environ.get("WORKFLOW_WEBHOOK_URL", "https://api-na1.hubapi.com/automation/v4/webhook-triggers/50831618/j6EloSG")
# Treatment Episode Workflow (2-54812380)
WORKFLOW_WEBHOOK_URL_EPISODE = os.environ.get("WORKFLOW_WEBHOOK_URL_EPISODE", "https://api-na1.hubapi.com/automation/v4/webhook-triggers/50831618/n3bB66h")

def get_hubspot_access_token():
    """
    Returns the HubSpot Access Token.
    Favor environment variable HUBSPOT_ACCESS_TOKEN if set (for local testing),
    otherwise fetch from Secret Manager.
    """
    local_token = os.environ.get("HUBSPOT_ACCESS_TOKEN")
    if local_token:
        return local_token
    
    return get_secret(HUBSPOT_SECRET_NAME, PROJECT_ID)

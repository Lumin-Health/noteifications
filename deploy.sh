#!/bin/bash

# Configuration
PROJECT_ID="lumininternal"
REGION="us-central1"
FUNCTION_NAME="hubspot-note-notifier"
ENTRY_POINT="handle_webhook"
RUNTIME="python310"
SECRET_NAME="Lumin-OS-Hubspot-API"
# Auth Workflow
WORKFLOW_WEBHOOK_URL="https://api-na1.hubapi.com/automation/v4/webhook-triggers/46446185/BfJsN4l"
# Treatment Episode Workflow
WORKFLOW_WEBHOOK_URL_EPISODE="TO_BE_UPDATED_PROD_EPISODE_WEBHOOK_URL"

if [ -z "$WORKFLOW_WEBHOOK_URL" ]; then
  echo "WARNING: WORKFLOW_WEBHOOK_URL is not set."
fi

echo "Deploying $FUNCTION_NAME to $PROJECT_ID..."

gcloud functions deploy $FUNCTION_NAME \
    --gen2 \
    --region=$REGION \
    --runtime=$RUNTIME \
    --source=. \
    --entry-point=$ENTRY_POINT \
    --trigger-http \
    --allow-unauthenticated \
    --project=$PROJECT_ID \
    --set-env-vars WORKFLOW_WEBHOOK_URL="$WORKFLOW_WEBHOOK_URL",WORKFLOW_WEBHOOK_URL_EPISODE="$WORKFLOW_WEBHOOK_URL_EPISODE",HUBSPOT_SECRET_NAME="$SECRET_NAME",GCP_PROJECT="$PROJECT_ID" \
    --service-account="reverse-etl-function-sa@lumininternal.iam.gserviceaccount.com"

echo "Deployment initiated. Check Cloud Console for status."

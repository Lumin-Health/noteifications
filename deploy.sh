#!/bin/bash

# Configuration
PROJECT_ID="lumininternal"
REGION="us-central1"
FUNCTION_NAME="hubspot-note-notifier"
ENTRY_POINT="handle_webhook"
RUNTIME="python310"
SECRET_NAME="hubspot-new-standard-sandbox-token"
# Auth Workflow
WORKFLOW_WEBHOOK_URL="https://api-na1.hubapi.com/automation/v4/webhook-triggers/50831618/j6EloSG"
# Treatment Episode Workflow
WORKFLOW_WEBHOOK_URL_EPISODE="https://api-na1.hubapi.com/automation/v4/webhook-triggers/50831618/n3bB66h"

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

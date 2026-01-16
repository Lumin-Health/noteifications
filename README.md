# HubSpot Note-ifications: Walkthrough

## Overview
The **HubSpot Note-ifications** system is a Google Cloud Function that listens for "Note Created" events from HubSpot. It evaluates whether the note's author is different from the associated object's owner (or if the object has no owner). If a mismatch is detecting (implying a notification is needed), it triggers a specific HubSpot Workflow via a Webhook.

## Architecture
- **Trigger**: HubSpot Webhook (Note Creation) -> Cloud Function URL.
- **Compute**: GCP Cloud Function (Gen 2) `hubspot-note-notifier`.
- **Logic**:
    1.  Receives Note ID.
    2.  Resolves Note Author.
    3.  Identifies Associated Object (Contact, Insurance Authorization, Treatment Episode).
    4.  Fetches Object Owner.
    5.  **Rule**: If `Author != Owner` OR `Owner is None` -> **Trigger**.
- **Output**: Sends enriched JSON payload to HubSpot Automation v4 Webhook.

## Configuration
### Environment Variables
| Variable | Description | Value |
| :--- | :--- | :--- |
| `WORKFLOW_WEBHOOK_URL` | Webhook for Auth Workflows | `.../j6EloSG` |
| `WORKFLOW_WEBHOOK_URL_EPISODE` | Webhook for Episode Workflows | `.../n3bB66h` |
| `HUBSPOT_SECRET_NAME` | GCP Secret for API Token | `hubspot-new-standard-sandbox-token` |

### Object Routing
| Object Type | Workflow Webhook |
| :--- | :--- |
| **Insurance Authorization** (`2-54811911`) | `WORKFLOW_WEBHOOK_URL` |
| **Treatment Episode** (`2-54812380`) | `WORKFLOW_WEBHOOK_URL_EPISODE` |

## Deployment
- **Repository**: [Lumin-Health/noteifications](https://github.com/Lumin-Health/noteifications)
- **GCP Project**: `lumininternal`
- **Region**: `us-central1`
- **Service Account**: `reverse-etl-function-sa`
- **Live URL**: `https://us-central1-lumininternal.cloudfunctions.net/hubspot-note-notifier`

## Verification
Verified successfully with live HubSpot data:

### Test Case 1: Insurance Authorization
- **Object**: `44816808554`
- **Note**: `101380571553`
- **Result**: Triggered `j6EloSG`

### Test Case 2: Treatment Episode
- **Object**: `44933152642`
- **Note**: `101391354421`
- **Result**: Triggered `n3bB66h`

## Production Migration Guide
When moving from Sandbox to Production, the **Webhook URLs will change**.

1.  **Migrate Workflows**: Recreate or import the two workflows (Auth & Episode) in your Production HubSpot Portal.
2.  **Get New Webhooks**: Open each workflow -> "Main Trigger" -> Copy the new Webhook URL.
3.  **Update GCP**:
    *   Go to [GCP Cloud Functions](https://console.cloud.google.com/functions/list?project=lumininternal).
    *   Select `hubspot-note-notifier` -> **Edit**.
    *   Update Runtime Environment Variables:
        *   `WORKFLOW_WEBHOOK_URL`: Paste new **Insurance Authorization** Webhook URL.
        *   `WORKFLOW_WEBHOOK_URL_EPISODE`: Paste new **Treatment Episode** Webhook URL.
    *   Update Secrets: Ensure `HUBSPOT_SECRET_NAME` points to a secret containing your **Production** Private App Access Token.
    *   **Deploy**.

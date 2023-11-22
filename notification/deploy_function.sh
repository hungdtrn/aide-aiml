#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. $SCRIPT_DIR/../set_env.sh

gcloud functions deploy notification-function \
  --gen2 \
  --trigger-http \
  --region=$FUNCTION_REGION \
  --source $NOTIFICATION_SRC \
  --entry-point=notification \
  --runtime python311 \
  --no-allow-unauthenticated \
  --service-account ${SCHEDULER_SERVICE_ACCOUNT}@${PROJECT}.iam.gserviceaccount.com

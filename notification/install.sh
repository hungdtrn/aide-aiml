#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. $SCRIPT_DIR/../set_env.sh

gcloud iam service-accounts create ${SCHEDULER_SERVICE_ACCOUNT}

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SCHEDULER_SERVICE_ACCOUNT}@${PROJECT}.iam.gserviceaccount.com" \
  --role="roles/run.invoker" \
  --role="roles/cloudscheduler.serviceAgent" \
  --role="roles/storage.admin"

gcloud storage buckets create gs://$BUCKET_NAME --project ${PROJECT} \
    --location $FUNCTION_REGION --default-storage-class=STANDARD

#gcloud functions delete notification-function --gen2 --quiet --project $PROJECT --region=$FUNCTION_REGION

sh $SCRIPT_DIR/deploy_frunction.sh

#gcloud scheduler jobs delete daily_notification-job --quiet --project $PROJECT --location $SCHEDULER_REGION

gcloud scheduler jobs create http daily_notification-job \
  --project $PROJECT \
  --location $SCHEDULER_REGION \
  --schedule "$SCHEDULE" \
  --time-zone "Australia/Sydney" \
  --uri "https://${FUNCTION_REGION}-${PROJECT}.cloudfunctions.net/notification-function" \
  --http-method POST \
  --message-body '{"name": "Scheduler"}' \
  --oidc-service-account-email ${SCHEDULER_SERVICE_ACCOUNT}@${PROJECT}.iam.gserviceaccount.com

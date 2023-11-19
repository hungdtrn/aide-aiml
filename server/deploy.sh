#!/usr/bin/env bash
SERVER_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. $SERVER_DIR/../set_env.sh

cp -r $SERVER_DIR/../ai $SERVER_DIR
gcloud run deploy aide-server --project $PROJECT --region=$REGION --allow-unauthenticated \
    --update-secrets=OPENAI_API_KEY=OPENAI_API_KEY:latest \
    --set-env-vars "MODEL=gpt-3.5-turbo" \
    --set-env-vars "BUCKET_NAME=${BUCKET_NAME}" \
    --source=$SERVER_DIR

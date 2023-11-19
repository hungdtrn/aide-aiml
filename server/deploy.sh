#!/usr/bin/env bash
SERVER_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. $SERVER_DIR/../set_env.sh

BUILD_DIR=$SERVER_DIR/../tmp_build
rm -fr $BUILD_DIR
mkdir $BUILD_DIR
cp -r $SERVER_DIR/../ai $BUILD_DIR
cp $SERVER_DIR/* $BUILD_DIR
gcloud run deploy aide-server --project $PROJECT --region=$REGION --allow-unauthenticated \
    --update-secrets=OPENAI_API_KEY=OPENAI_API_KEY:latest \
    --set-env-vars "MODEL=gpt-3.5-turbo" \
    --set-env-vars "BUCKET_NAME=${BUCKET_NAME}" \
    --source=$BUILD_DIR
rm -fr $BUILD_DIR
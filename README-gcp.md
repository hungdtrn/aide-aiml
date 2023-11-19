# GCP


### Initial GCP environment setup:
```
. set_env.sh
gcloud config set project $PROJECT
gcloud services enable \
    compute.googleapis.com \
    secretmanager.googleapis.com \
    artifactregistry.googleapis.com
```

### Create GCP Secret OPENAI_API_KEY and add IAM policy for service account access to the secret:
```
OPENAI_API_KEY=🔥<OPENAI_API_KEY>🔥
. set_env.sh
echo -n $OPENAI_API_KEY | gcloud secrets create OPENAI_API_KEY --project $PROJECT --data-file=-

gcloud projects add-iam-policy-binding $PROJECT \
    --member=serviceAccount:${PROJECT_ID}-compute@developer.gserviceaccount.com \
    --role=roles/secretmanager.secretAccessor \
    --role=roles/iam.serviceAccountUser \
    --role=roles/storage.admin
```


## Deploy to Cloud Run:
```
./server/deploy.sh
```


## Clean Up
```
. set_env.sh
gcloud run services delete aide-server --quiet --project $PROJECT --region=$REGION
```
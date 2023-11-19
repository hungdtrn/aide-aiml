#export OPENAI_API_KEY

export PROJECT=
#PROJECT_ID=$(gcloud projects describe $PROJECT --format='value(projectNumber)')
echo PROJECT_ID: $PROJECT_ID
export PROJECT_ID=
export REPO_HOME=~/git/aide-aiml

#MODEL=gpt-4
export MODEL=gpt-3.5-turbo
export BUCKET_NAME=${PROJECT}-aide

export REGION=australia-southeast2

gcloud config set project $PROJECT &

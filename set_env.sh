#export OPENAI_API_KEY

export PROJECT=aide-aiml
#PROJECT_ID=$(gcloud projects describe $PROJECT --format='value(projectNumber)')
echo PROJECT_ID: $PROJECT_ID
export PROJECT_ID=144023999182
export REPO_HOME=~/git/aide-aiml

#MODEL=gpt-4
export MODEL=gpt-3.5-turbo
export BUCKET_NAME=joe-aide

export REGION=australia-southeast2

gcloud config set project $PROJECT &

#export OPENAI_API_KEY
#export MAILGUN_API_KEY

export PROJECT=aide-aiml
#PROJECT_ID=$(gcloud projects describe $PROJECT --format='value(projectNumber)')
echo PROJECT_ID: $PROJECT_ID
export PROJECT_ID=144023999182
export REPO_HOME=~/git/aide-aiml

#MODEL=gpt-4
export MODEL=gpt-3.5-turbo
export BUCKET_NAME=joe-aide
export SCHEDULE="0 * * * *"
export NOTIFICATION_SRC=$REPO_HOME/notification

# Function region requires gen2 that is only in southeast2
export FUNCTION_REGION=australia-southeast2

# Scheduler region requires southeast1 
export SCHEDULER_REGION=australia-southeast1

export REGION=$FUNCTION_REGION

export SCHEDULER_SERVICE_ACCOUNT=aide-scheduler-job-sa
gcloud config set project $PROJECT &

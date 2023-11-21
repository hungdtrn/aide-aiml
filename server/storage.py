import json
import os
import datetime
from google.cloud import storage

# Only use GCS bucket when BUCKET_NAME is defined, otherwise use local storage 
USE_BUCKET = "BUCKET_NAME" in os.environ

STORAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "./localStorage")
DUMMY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "./initialData")

def bucket():
    return storage.Client().bucket(os.environ.get('BUCKET_NAME'))

def blob(blob_name):
    return bucket().blob(blob_name)

def upload(blob_name, content):
    """  Add ${content} to the file wih the path ${blob_name}
    """
    if USE_BUCKET:
        blob(blob_name).upload_from_string(content)
    else:
        with open(os.path.join(STORAGE_PATH, blob_name), "w") as f:
            json.dump(json.loads(content), f)

def download(destination_blob_name):
    """ Load the content of a file with the path destination_blob_name
    """
    if USE_BUCKET:
        return blob(destination_blob_name).download_as_string().decode("utf-8")
    else:
        with open(os.path.join(STORAGE_PATH, destination_blob_name), "r") as f:
            return json.load(f)

def writeUser(userId, user):    
    upload(f"user/{userId}.json", json.dumps(user, indent=2))
    writeConversation(userId, [])
    writeDailySummary(userId, [])   
    writeDevSummary(userId, [])
    writeindicator(userId, [])
    writeMedicalInput(userId, [])
    writeCarerInput(userId, [])

def writeConversation(userId, conversation):
    upload(f"conversation/{userId}.json", json.dumps(conversation, indent=2))

def writeDailySummary(userId, dailySummary):
    upload(f"dailySummary/{userId}.json", json.dumps(dailySummary, indent=2))

def writeDevSummary(userId, developmentSummary):
    upload(f"developmentSummary/{userId}.json", json.dumps(developmentSummary, indent=2))

def writeindicator(userId, indicator):
    upload(f"indicator/{userId}.json", json.dumps(indicator, indent=2))

def writeMedicalInput(userId, medicalInput):
    upload(f"medicalInput/{userId}.json", json.dumps(medicalInput, indent=2))

def writeCarerInput(userId, carerInput):
    upload(f"carerInput/{userId}.json", json.dumps(carerInput, indent=2))

def readUser(userId):
    return download(f"user/{userId}.json")

def readConversation(userId):
    return download(f"conversation/{userId}.json")

def readDailySummary(userId):
    return download(f"dailySummary/{userId}.json")

def readDevSummary(userId):
    return download(f"developmentSummary/{userId}.json")

def readIndicator(userId):
    return download(f"indicator/{userId}.json")

def readMedicalInput(userId):
    return download(f"medicalInput/{userId}.json")

def readCarerInput(userId):
    return download(f"carerInput/{userId}.json")

# def writeHistory(userId, history):
#     upload(f"history/{userId}.json", json.dumps(history, indent=2))

# # def writeIndicators(userId, indicators):
# #     upload(f"indicators/{userId}.json", json.dumps(indicators, indent=2))

# def readHistory(userId):
#     return download(f"history/{userId}.json")

# # def readIndicators(userId):
# #     """
# #     Read JSON containing indicator scores
# #     """
# #     return download(f"indicators/{userId}.json")

if __name__ == "__main__":
    readUser("-1")
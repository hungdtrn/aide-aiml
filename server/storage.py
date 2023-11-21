import json
import os


STORAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "./localStorage")

def writeUser(userId, user):
    upload(f"user/{userId}.json", json.dumps(user, indent=2))

def writeHistory(userId, history):
    upload(f"history/{userId}.json", json.dumps(history, indent=2))

# def writeIndicators(userId, indicators):
#     upload(f"indicators/{userId}.json", json.dumps(indicators, indent=2))

def readHistory(userId):
    return download(f"history/{userId}.json")

# def readIndicators(userId):
#     """
#     Read JSON containing indicator scores
#     """
#     return download(f"indicators/{userId}.json")

def upload(blob_name, content):
    """  Add ${content} to the file wih the path ${blob_name}
    """
    with open(os.path.join(STORAGE_PATH, blob_name), "w") as f:
        json.dump(json.loads(content), f)

def download(destination_blob_name):
    """ Load the content of a file with the path destination_blob_name
    """
    with open(os.path.join(STORAGE_PATH, destination_blob_name), "r") as f:
        return json.load(f)

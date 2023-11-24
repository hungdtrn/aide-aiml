import os
from dotenv import load_dotenv
import requests
import json
load_dotenv()
if os.getenv("APPLICATION_SERVER")=="GCP":
    server_url = os.getenv("GCP_SERVER_URL")
else:
    server_url = os.getenv("LOCAL_SERVER_URL")


CACHE_NUM_ENTRY = 1
CACHE_TTL = 10

def set_url(url):
    """
    Set url for tests as global variables
    """
    global server_url
    server_url = url


def post(path, server_url, obj, stream=False):
    """
    Funtion for POST requests. This function can also handle streaming requests.
    When streaming, set stream == True
    """
    headers = {'Content-type': 'application/json'}
    response = requests.post(f"{server_url}/{path}", data=json.dumps(obj), headers=headers, stream=stream)
    if not response.ok:
        print(response.text)
        raise Exception(f"Invalid response: {response.text}")

    # Return appropriate outputs depending on whether or not the response is streamed.
    if stream:
        return response.iter_content(None)
    else:
        return json.loads(response.text)

def welcome(obj):
    """
    Welcome function used for for user starting a session
    """
    return post("welcome", server_url, obj)

def welcome_stream(obj):
    """
    Welcome function used for for user starting a session
    """
    obj["streaming"] = True
    return post("welcome", server_url, obj, stream=True)


def dailySummary(obj):
    """
    DailySummary function used for for user pulling through a dailySummary
    """
    return post("dailySummary", server_url, obj)

def dailyIndicator(obj):
    """
    DailyIndicator function used for for user pulling through the medical indicators
    """
    return post("indicator", server_url, obj)

def chatStream(obj):
    """
    chatStream function used for generating chats
    """
    obj["streaming"] = True
    return post("chat", server_url, obj, stream=True)

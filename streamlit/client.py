import requests
import json

# server_url = "http://127.0.0.1:8080"
server_url = "https://aide-server-ogdrzymura-km.a.run.app"
# Write util files here such as createUser, chat, post and server url

def set_url(url):
    """
    Set url for tests as global variables
    """
    global server_url
    server_url = url


def post(path, server_url, obj):
    headers = {'Content-type': 'application/json'}
    response = requests.post(f"{server_url}/{path}", data=json.dumps(obj), headers=headers)
    if not response.ok:
        print(response.text)
        raise Exception(f"Invalid response: {response.text}")

    return json.loads(response.text)

def stream(path, obj):
    # CODE FOR STREAMING REQUESTS. Use when we want to stream token by token instead of showing the whole sentence.
    headers = {'Content-type': 'application/json'}
    response = requests.post(f"{server_url}/{path}", data=json.dumps(obj), headers=headers, stream=True)
    if not response.ok:
        print(response.text)
        raise Exception(f"Invalid response: {response.text}")

    return response.iter_content(None)

def welcome(obj):
    """
    Welcome function used for for user starting a session
    """
    return post("welcome", server_url, obj)

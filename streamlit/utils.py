import requests
import json

server_url = "http://127.0.0.1:8080"

# Write util files here such as createUser, chat, post and server url
def post(path, obj):
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
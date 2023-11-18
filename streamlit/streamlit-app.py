import streamlit as st
import requests
import json
# from utils import createUser, chat, post
# Page title
st.title("AIDE")

server_url = "http://127.0.0.1:8080"
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
# Server URL

# response
# userId

# First prompt
#prompt = st.text_input("Start journaling your thoughts")

# Button
# ------------------- Hung implementation ------------------
# Just for demo how we use the summary API
if st.button('Summary'):
   response = post("summary", {"userId": 0})
   st.write(json.dumps(response, indent=2))
 
#Initialise the chat session in the server and get the display message
message = st.chat_message("assistant")
message.write(post("welcome", {"userId": 0})["msg"])   

# Streaming the chat
prompt = st.chat_input("Response.......")
if prompt:
    out_stream = stream("chat_stream", {'userId': 0, 'message': prompt})
    for line in out_stream:
        # we get the output tokens by tokens, and we show them one by one
        st.write(line.decode("utf-8"))


# # If we don't want streaming, just use the previous code
# prompt = st.chat_input("Response.......")
# if prompt:
#     st.write(f"{post('chat', {'userId': 0, 'message': prompt})['msg']}")

# ------------------- End Hung's implementation ------------------

#building out chat history
if "messages" not in st.session_state:
    st.session_state.messages = []



# response =
# Print response

import streamlit as st
import requests
import json
# from utils import createUser, chat, post
# Page title
st.title("AIDe")

server_url = "http://127.0.0.1:8080"
def post(path, obj):
    headers = {'Content-type': 'application/json'}
    response = requests.post(f"{server_url}/{path}", data=json.dumps(obj), headers=headers)
    if not response.ok:
        print(response.text)
        raise Exception(f"Invalid response: {response.text}")
    
    return json.loads(response.text)
# Server URL

# response
# userId

# First prompt
#prompt = st.text_input("Start journaling your thoughts")

# Button
#if st.button('Generate response'):
#    response = "TEST STRING Sorry to hear that"
#    st.write(response)
 
#Promt for Asking for a response 
message = st.chat_message("assistant")
post("createUser", {"userId": 0})
message.write(post("welcome", {"userId": 0})["msg"])   
    
# Creating out a chat input
prompt =  st.chat_input("Response.......")
if prompt:
    st.write(f"{prompt}")
    
#building out chat history
if "messages" not in st.session_state:
    st.session_state.messages = []



# response =
# Print response

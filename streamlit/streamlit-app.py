import streamlit as st
import requests
import json
from utils import createUser, chat, post, stream
# Page title
st.title("AIDE")

server_url = "http://127.0.0.1:8080"


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
prompt = st.chat_input("Type Message.......")
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

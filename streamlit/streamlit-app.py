import streamlit as st
import requests
import json
from utils import post, stream
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

#building out chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

#Initialise the chat session in the server and get the display message
message = st.chat_message("assistant")
message.write(post("welcome", {"userId": 0})["msg"])

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Streaming the chat
prompt = st.chat_input("Type Message.......")

# # If we don't want streaming, just use the previous code
# prompt = st.chat_input("Response.......")
# if prompt:
#     st.write(f"{post('chat', {'userId': 0, 'message': prompt})['msg']}")

# ------------------- End Hung's implementation ------------------
 

# Implementation of the chat history and containerized conversation
if prompt:
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    out_stream = stream("chat_stream", {'userId': 0, 'message': prompt})
    #st.chat_message("user").write(prompt)
    x = []
    for line in out_stream:
        x.append(line.decode("utf-8"))
    response = ''.join(x)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})



# response =
# Print response

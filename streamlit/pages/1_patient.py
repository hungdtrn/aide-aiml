import streamlit as st
import requests
import json
from utils import post, stream
# Page title
st.title("AIDE")
st.text("Patient page")

# NOTE -  This code was copied from streamlit-app.py on 20 Nov at 10:45 am.
# It's not reflective of the current version, for testing purposes only


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

    with st.chat_message("assistant"):
        # Creating an empty array to store stream text
        report = []
        res_box = st.empty() # create an empty box
        ## Joes Implementation for stream chat
        for line in out_stream:
            # we get the output tokens by tokens, and we show them one by one
            report.append(line.decode("utf-8"))# append the token to the report list
            # Clean the string
            result = "".join(report).strip()
            result= result.replace("\n","")
            res_box.markdown(f'*{result}*')

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": f'*{result}*'})

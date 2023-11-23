import streamlit as st
import requests
import json
from client import welcome, post, chatStream
import types

# Page title
st.title("AIDE")
st.text("Patient page")


#building out chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

@st.cache_data
def starting_application():
    return welcome(obj = {"userId": 0, "streaming": False})
    
#Initialise the chat session in the server and get the display message
# Load the welcome message only once
try:
    welcome_msg = starting_application()
    message = st.chat_message("assistant")
    message.write(welcome_msg["response"])
except Exception as e:
    message.write("Apologies we seem to be having internal issues, We are trying to fix this currently. Thank you for your patience")


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Streaming the chat
prompt = st.chat_input("Type Message.......")


# Implementation of the chat history and containerized conversation
if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    try:
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        out_stream = chatStream({'userId': 0, 'message': prompt})
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
    except Exception as e:
        print(e) ## Need to add error log to server
        st.text(e)
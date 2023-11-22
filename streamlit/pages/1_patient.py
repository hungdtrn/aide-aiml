import streamlit as st
import requests
import json
from utils import post, stream
from client import welcome
# Page title
st.title("AIDE")
st.text("Patient page")


#building out chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

#Initialise the chat session in the server and get the display message
message = st.chat_message("assistant")
try:
    message.write(welcome(obj = {"userId": 0})["response"])
except:
    message.write("Apologies we seem to be having internal issues, We are trying to fix this currently. Thank you for your patience")

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
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    try:
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
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
    except:
        print('') ## Need to add error log to server

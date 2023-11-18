import streamlit as st
import requests
import json
# from utils import createUser, chat, post
# Page title
st.title("AIDe")


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
message.write("Hi how may I help you")   
    
# Creating out a chat input
prompt =  st.chat_input("Response.......")
if prompt:
    st.write(f"{prompt}")
    
#building out chat history
if "messages" not in st.session_state:
    st.session_state.messages = []



# response =
# Print response

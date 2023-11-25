import streamlit as st
import requests
import json
from client import welcome, get_chat_history, CACHE_NUM_ENTRY, CACHE_TTL
import types

# Page title
st.title("AIDE")
st.text("Patient page")


#building out chat history
if "messages" not in st.session_state:
    st.session_state.history_messages = []

@st.cache_data(ttl=CACHE_TTL)
def  load_chat_history(userID, date):
    lines = get_chat_history(obj = {"userId": userID, "date": date})["response"]
    out = []
    for line in lines:
        line = line["content"]
        for k, v in line.items():
            out.append({"role": k, "content": v})
    
    return out
    

userID = st.text_input('PatientID', 0)
date = st.text_input('Date', "2023-11-24")

if userID and date:
    st.session_state.history_messages = load_chat_history(userID, date)
    for message in st.session_state.history_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


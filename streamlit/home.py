import os
from dotenv import load_dotenv
import streamlit as st
load_dotenv()
st.title("AIDE")
st.text("The AI for supporting elderly people with dementia and other mental impariments")
st.text(f"Application server deployed on:{os.getenv('APPLICATION_SERVER')}")

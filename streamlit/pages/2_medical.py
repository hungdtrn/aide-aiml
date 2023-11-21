import streamlit as st
from utils import post
import requests
import json
import pandas as pd
import datetime

st.title("AIDE")
st.text("Medical page")


# Just for demo how we use the summary API
userID = st.text_input('PatientID', None)

# if st.button('Summary'):
#     try:
#         response = post("summary", {"userId": userID})

#         df = pd.DataFrame(response['history']) # Create a dataframe for the history
#         df_summary= df[['date', 'developmentSummary']].tail(5) # Take the last 5 entries
#         df_summary.loc[:, 'date'] = df_summary['date'].map(lambda x : datetime.datetime.utcfromtimestamp(x)) # Convert to date time

#         tab1, tab2, tab3, tab4, tab5 = st.tabs(df_summary['date'].to_list()) # Pass in the datetimes as tab headers

#         tab_list = [tab1, tab2, tab3, tab4, tab5] # create a tab list

#         # Populate the tabs
#         for i in range(len(tab_list)):
#             with tab_list[i]:
#                 st.header(df_summary['date'].iloc[i])
#                 st.text(df_summary['developmentSummary'].iloc[i])
#     except:
#         st.write("User does not exist")

if st.button('Summary'):

    response = post("summary", {"userId": userID})

    df = pd.DataFrame(response['history']) # Create a dataframe for the history
    df_summary= df[['date', 'developmentSummary']].tail(5) # Take the last 5 entries
    df_summary.loc[:, 'date'] = df_summary.loc[:, 'date'] = df_summary['date'].map(lambda x : str(pd.to_datetime(datetime.datetime.utcfromtimestamp(x)).date()))# Convert to date time # Convert to date time

    tab1, tab2, tab3, tab4, tab5 = st.tabs(df_summary['date'].to_list()) # Pass in the datetimes as tab headers

    tab_list = [tab1, tab2, tab3, tab4, tab5] # create a tab list

    # Populate the tabs
    for i in range(len(tab_list)):
        with tab_list[i]:
            st.header(df_summary['date'].iloc[i])
            st.text(df_summary['developmentSummary'].iloc[i])

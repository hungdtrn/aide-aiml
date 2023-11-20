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

if st.button('Summary'):
    response = post("summary", {"userId": userID})

    # Create a dataframe for the history
    df = pd.DataFrame(response['history'])
    df_summary= df[['date', 'developmentSummary']]
    df_summary.loc[:, 'date'] = df_summary['date'].map(lambda x : datetime.datetime.utcfromtimestamp(x))

    # Display the table
    st.table(df_summary)

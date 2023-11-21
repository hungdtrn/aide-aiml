import streamlit as st
from utils import post
import requests
import json
import pandas as pd
import datetime
import streamlit_scrollable_textbox as stx
import matplotlib.pyplot as plt

st.title("AIDE")
st.text("Medical page")
st.header("Medical summary")


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

if st.checkbox('View daily Summary'):

    response = post("retrievesummary", {"userId": userID})

    df = pd.DataFrame(response['history']) # Create a dataframe for the history
    df_summary= df[['date', 'developmentSummary']].tail(5).fillna("No information") # Take the last 5 entries, and fill NaN
    df_summary.loc[:, 'date'] = df_summary.loc[:, 'date'] = df_summary['date'].map(\
                                    lambda x : str(pd.to_datetime(datetime.datetime.utcfromtimestamp(x)).date())\
                                        )# Convert to date time



    tab1, tab2, tab3, tab4, tab5 = st.tabs(df_summary['date'].to_list()) # Pass in the datetimes as tab headers

    tab_list = [tab1, tab2, tab3, tab4, tab5] # create a tab list

    # Populate the tabs
    for i in range(len(tab_list)):
        with tab_list[i]:
            st.header(df_summary['date'].iloc[i])
            stx.scrollableTextbox(text = df_summary['developmentSummary'].iloc[i], border= True, key = i)


if st.checkbox('View Indicator Trends'):
    #--- Indicator trends---#
    st.header("Indicator Trends")


    # Create mock dates
    dates = []
    for i in range(5):
        datetime_str = f'2{i}/11/23'
        dates.append(datetime.datetime.strptime(datetime_str, '%d/%m/%y'))

    # Create mock indicator data
    df_indicators = pd.DataFrame()
    df_indicators['date'] = dates
    df_indicators['mentalHealth'] = [5,4,5,3,4]
    df_indicators['socialHealth'] = [3, 3, 4, 5,5]
    df_indicators['physicalHealth'] = [3,4,5,5,4]
    date = df_indicators['date']
    values = df_indicators[['mentalHealth','socialHealth','physicalHealth']]

    # Create radio buttons for graph
    indicator = st.radio(
        "Please select an indicator to view trend",
        ["Mental health", "Social health", "Physical health", "All"])

    if indicator == 'Mental health':
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(df_indicators['date'], df_indicators['mentalHealth'], label = 'Mental Health', color = 'blue' )
        ax.set_ylim(0,5.5)
        ax.set_xlabel('Date')
        ax.legend()
        # Display plot
        st.pyplot(fig)

    elif indicator == 'Social health':
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(df_indicators['date'], df_indicators['socialHealth'], label = 'Social Health', color = 'green')
        ax.set_ylim(0,5.5)
        ax.set_xlabel('Date')
        ax.legend()

        # Display plot
        st.pyplot(fig)

    elif indicator == 'Physical health':
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(df_indicators['date'], df_indicators['physicalHealth'], label = 'Physical Health', color = 'orange')
        ax.set_ylim(0,5.5)
        ax.set_xlabel('Date')
        ax.legend()

        # Display plot
        st.pyplot(fig)

    else:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(df_indicators['date'], df_indicators['mentalHealth'], label = 'Mental Health', color = 'blue' )
        ax.plot(df_indicators['date'], df_indicators['socialHealth'], label = 'Social Health', color = 'green')
        ax.plot(df_indicators['date'], df_indicators['physicalHealth'], label = 'Physical Health', color = 'orange')
        ax.set_xlabel('Date')
        ax.set_ylim(0,5.5)
        ax.legend()

        # Display plot
        st.pyplot(fig)

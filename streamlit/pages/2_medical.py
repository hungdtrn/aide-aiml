import streamlit as st
from client import dailySummary, dailyIndicator, CACHE_NUM_ENTRY, CACHE_TTL
import requests
import json
import pandas as pd
import datetime
import streamlit_scrollable_textbox as stx
import matplotlib.pyplot as plt

st.title("AIDE")
st.text("Medical page")
st.header("Medical summary")

@st.cache_data(ttl=CACHE_TTL)
def querying_summary():
    return dailySummary(obj =  {"userId": userID, "n" : num_tabs})

@st.cache_data(ttl=CACHE_TTL)
def quyerying_indicator():
    return dailyIndicator(obj = {"userId": userID, "n" : 5})



# Just for demo how we use the summary API
userID = st.text_input('PatientID', None)
checkbox_disabled = True # Disable the checkboxes by default
if userID:
    # Need to also put in a check for a valid userID
    checkbox_disabled= False
else:
    st.text("Enter user ID")

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

if st.checkbox('View daily Summary', disabled = checkbox_disabled):

    num_tabs = 5
    response = querying_summary()
    df = pd.DataFrame.from_dict(response['response'])
    # Check dataframe length, and if shorter than n, return only that many tabs
    if len(df) < num_tabs:
        num_tabs = len(df)


    df_summary= df[['date', 'summary']].tail(num_tabs).fillna("No information") # Take the appropriate number of tabs
    df_summary = df_summary.replace('', 'No information')

    # Convert the 'date' column to datetime
    df_summary['date'] = pd.to_datetime(df_summary['date'])

    # Update the 'date' column with the date in string format
    df_summary['date'] = df_summary['date'].dt.date.astype(str)

    tab_list = st.tabs(df_summary['date'].to_list()) # Pass in the datetimes as tab headers

    # Populate the tabs
    for i in range(len(tab_list)):
        with tab_list[i]:
            st.header(df_summary['date'].iloc[i])
            stx.scrollableTextbox(text = df_summary['summary'].iloc[i], border= True, key = i)


if st.checkbox('View Indicator Trends', disabled = checkbox_disabled):
    try:
        indicator = quyerying_indicator()
        #--- Indicator trends---#
        st.header("Indicator Trends")


        df_indicators = pd.DataFrame.from_dict(indicator['response'])
        df_indicators[['mental_health','physical_health','social_health']] = df_indicators['indicators'].apply(pd.Series)

        # Create radio buttons for graph
        indicator = st.radio(
            "Please select an indicator to view trend",
            ["Mental health", "Social health", "Physical health", "All"])

        if indicator == 'Mental health':
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot(df_indicators['date'], df_indicators['mental_health'], label = 'Mental Health', color = 'blue' )
            ax.set_ylim(0,5.5)
            ax.set_xlabel('Date')
            ax.legend()
            # Display plot
            st.pyplot(fig)

        elif indicator == 'Social health':
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot(df_indicators['date'], df_indicators['social_health'], label = 'Social Health', color = 'green')
            ax.set_ylim(0,5.5)
            ax.set_xlabel('Date')
            ax.legend()

            # Display plot
            st.pyplot(fig)

        elif indicator == 'Physical health':
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot(df_indicators['date'], df_indicators['physical_health'], label = 'Physical Health', color = 'orange')
            ax.set_ylim(0,5.5)
            ax.set_xlabel('Date')
            ax.legend()

            # Display plot
            st.pyplot(fig)

        else:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot(df_indicators['date'], df_indicators['mental_health'], label = 'Mental Health', color = 'blue' )
            ax.plot(df_indicators['date'], df_indicators['social_health'], label = 'Social Health', color = 'green')
            ax.plot(df_indicators['date'], df_indicators['physical_health'], label = 'Physical Health', color = 'orange')
            ax.set_xlabel('Date')
            ax.set_ylim(0,5.5)
            ax.legend()

            # Display plot
            st.pyplot(fig)
    except:
        st.text("Indicators not available")

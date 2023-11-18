import streamlit as st

# Page title
st.title("AIDe")


# First prompt
prompt = st.text_input("Start journaling your thoughts")

# Button
if st.button('Generate response'):
    #response code here
    response = 'Sorry to hear that. Please tell me more'
    st.write(response)

# response =
# Print response

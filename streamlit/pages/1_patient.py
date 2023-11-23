import streamlit as st
import requests
import json
from client import welcome, post, chatStream
# Page title
st.title("AIDE")
st.text("Patient page")

def streaming(output_stream):
    with st.chat_message("assistant"):
        # Creating an empty array to store stream text
            report = []
            res_box = st.empty() # create an empty box
            ## Joes Implementation for stream chat
            for line in output_stream:
                # we get the output tokens by tokens, and we show them one by one
                report.append(line.decode("utf-8"))# append the token to the report list
                # Clean the string
                result = "".join(report).strip()
                result= result.replace("\n","")
                res_box.markdown(f'*{result}*')

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": f'*{result}*'})

#building out chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.welcomed = False
    
    

#Initialise the chat session in the server and get the display message
if "welcomed" not in st.session_state or not st.session_state.welcomed:
    try:
        welcome_stream = welcome(obj = {"userId": 0, "streaming": True})
        st.session_state.welcomed = True
        streaming(welcome_stream)
    except Exception as e:
        print(e)
    # except Exception as e:
        # message.write(e)
        # message = st.chat_message("assistant")
        # message.write("Apologies we seem to be having internal issues, We are trying to fix this currently. Thank you for your patience")


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
        out_stream = chatStream({'userId': 0, 'message': prompt})
        #st.chat_message("user").write(prompt)
        streaming(out_stream)

    except Exception as e:
        print(e) ## Need to add error log to server
        st.text(e)

import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import time

# log string:
if 'transcript' not in st.session_state:
    st.session_state['transcript'] = ''

if 'username' not in st.session_state:
    st.session_state['username'] = ''

if 'password' not in st.session_state:
    st.session_state['password'] = ''

if 'login' not in st.session_state:
    st.session_state['login'] = False

# holds usernames and passwords
users = {"admin": "pass"}

# App title
st.set_page_config(page_title="GritGPT")

# login
with (st.sidebar):
    if st.session_state.login:
        logout = st.button(label="Logout")

        # note that they logged out and refresh
        if logout:
            st.session_state.login = False
            st.session_state.username = ""
            st.session_state.password = ""
            st.rerun()

    # if not logged in
    if not st.session_state.login:
        with st.form(key='user/pass', clear_on_submit=True):
            st.title('GritGPT')

            st.session_state.username = st.text_input(label="Username")
            st.session_state.password = st.text_input(label="Password", type="password")
            col1, col2, col3 = st.columns([0.2, 0.3, 0.5])
            with col3:
                submit = st.form_submit_button(label="Submit")
                # if I just hit submit refresh with new login value
                if submit and st.session_state.username in users and users.get(st.session_state.username) == st.session_state.password:
                    st.session_state.login = True;
                    st.rerun()



# if they entered the right password
if st.session_state.username in users and users.get(st.session_state.username) == st.session_state.password:
    st.session_state.login = True;
    refresh = False
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.title("Welcome to GritGPT!")
        st.text("Please ask any questions about UMBC")

    with col2:
        refresh = st.button(label="↻", help="Refresh")

    if refresh:
        del st.session_state["messages"]
        st.session_state.transcript = ""

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []



    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # get user input
    prompt = st.chat_input("Ask a question")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

    # calls the API for chatbase
    url = 'https://www.chatbase.co/api/v1/chat'
    headers = {
        'Authorization': 'Bearer 2781fc96-deab-45d8-9645-41860db1abda',
        'Content-Type': 'application/json'
    }
    data = {
        "messages": [
            #{"content": "How can I help you?", "role": "assistant"},
            {"content": prompt, "role": "user"}
        ],
        "chatbotId": "y7TCeYeI15zVWaowOeeRW",
        "stream": False,
        "temperature": 0
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    json_data = response.json()

    if response.status_code == 200:
        if json_data['text'] == "There is no documentation for this":
            file = open("log.txt", 'a')
            file.write(prompt + "\n")
            file.close()

        # add new response to transcript
        st.session_state.transcript = st.session_state.transcript + "User: " + prompt + "\n" + "GritGPT: " + json_data['text'] + "\n"

        with st.chat_message("assistant", avatar='./chip_pic.PNG'):
            message_placeholder = st.empty()
            full_response = ""
            bot_resp = json_data['text']

            # gives a slight delay
            for chunk in bot_resp.split():
                full_response += chunk + " "
                time.sleep(0.05)
                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(full_response + "▌")
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    else:
      print('Error:' + json_data['message'])

    with col2:
        st.download_button(label="📥", data=st.session_state.transcript, file_name="GritGPT_transcript.txt", help="Transcript")

elif submit:
    with (st.sidebar):
        st.error("Incorrect username or password")


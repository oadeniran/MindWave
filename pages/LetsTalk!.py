import streamlit as st
import os
import re
import random
import traceback
import streamlit as st
from dotenv import load_dotenv
from streamlit_chat import message
import chatbot
from core import rantSessions, userActions
import utils
import uuid
from config import OPENAI_API_KEY, EMBED_PATH

if 'uid' not in st.session_state:
    st.info("Please sign up/ login to continue")
else:
    
    if "input_message_key" not in st.session_state:
            st.session_state["input_message_key"] = str(random.random())
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = str(uuid.uuid4())
        userActions.add_user_session(st.session_state["uid"], st.session_state["session_id"], "Talk_session",{})

    PATH_TO_LOAD = f"{EMBED_PATH}/{st.session_state['uid']}"

    if 'rant_session' not in st.session_state:
        st.session_state['rant_session'] = {
            'past': [],
            'generated': []
        }
    st.title("HI, Let's Talk!")
    placeholder = st.empty()
    chat_container = placeholder.container()
    if len(st.session_state['rant_session']["generated"]) > 0:
        with chat_container:
            for i in range(len(st.session_state['rant_session']["generated"])):
                if i >= 1:
                    message(st.session_state['rant_session']["past"][i-1], is_user=True, key=str(i) + "_user")
                message(st.session_state['rant_session']["generated"][i], key=str(i))

    if len(st.session_state['rant_session']['generated']) < 1:
            output = rantSessions.talkToMe(st.session_state['uid'], st.session_state['session_id'], "", OPENAI_API_KEY, PATH_TO_LOAD)
            st.session_state['rant_session']["generated"].append(output)
            st.session_state["input_message_key"] = str(random.random())
            st.rerun()
    else:
        user_input = st.text_input("Type in your message", key=st.session_state["input_message_key"])
        if st.button("Send") and user_input != "":
            output = rantSessions.talkToMe(st.session_state['uid'], st.session_state['session_id'], user_input, OPENAI_API_KEY, PATH_TO_LOAD)
            st.session_state['rant_session']["past"].append(user_input)
            print("past", st.session_state['rant_session']["past"])
            st.session_state['rant_session']["generated"].append(output)
            st.session_state["input_message_key"] = str(random.random())
            st.rerun()
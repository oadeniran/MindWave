import streamlit as st

@st.cache_resource
def get_all_imports():
    import random
    from streamlit_chat import message
    from core import rantSessions, userActions
    import utils
    import uuid
    from config import OPENAI_API_KEY
    return random, message, rantSessions, userActions, utils, uuid, OPENAI_API_KEY


random, message, rantSessions, userActions, utils, uuid, OPENAI_API_KEY = get_all_imports()


if 'uid' not in st.session_state or st.session_state["uid"] == "":
    #st.info("Please sign up/ login to continue")
    st.session_state["uid"] = str(uuid.uuid4())+'-demo' # for demo purposes
    st.info("You are in demo mode. Your session will not be saved")
    st.rerun()
else:
    if "input_message_key" not in st.session_state:
            st.session_state["input_message_key"] = str(random.random())
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = str(uuid.uuid4())
        userActions.add_user_session(st.session_state["uid"], st.session_state["session_id"], "Talk_session",{})

    if 'rant_session' not in st.session_state:
        st.session_state['rant_session'] = {
            'past': [],
            'generated': [],
            'reports_doc_list': rantSessions.get_reports_doc_list(userActions.get_user_reports(st.session_state["uid"]), st.session_state['session_id'])
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
            output = rantSessions.talkToMe(st.session_state['uid'], st.session_state['session_id'], "", OPENAI_API_KEY, st.session_state['rant_session']['reports_doc_list'])
            st.session_state['rant_session']["generated"].append(output)
            st.session_state["input_message_key"] = str(random.random())
            utils.remove_embedded_data(st.session_state['session_id'])
            st.rerun()
    else:
        user_input = st.text_input("Type in your message", key=st.session_state["input_message_key"])
        if st.button("Send") and user_input != "":
            output = rantSessions.talkToMe(st.session_state['uid'], st.session_state['session_id'], user_input, OPENAI_API_KEY, st.session_state['rant_session']['reports_doc_list'])
            st.session_state['rant_session']["past"].append(user_input)
            print("past", st.session_state['rant_session']["past"])
            st.session_state['rant_session']["generated"].append(output)
            utils.remove_embedded_data(st.session_state['session_id'])
            st.session_state["input_message_key"] = str(random.random())
            st.rerun()
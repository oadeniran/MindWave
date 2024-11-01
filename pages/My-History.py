import streamlit as st
from core import userActions, chatActions
from streamlit_chat import message

def display_session_chat(chats, count):
    placeholder = st.empty()
    chat_container = placeholder.container()
    if count > 0:
        with chat_container:
            for chat in chats:
                if chat["message"] != "":
                    message(chat["message"], is_user=chat["type"]=="user")
    else:
        st.error("NO MESSAGES FOR THIS SESSION YET")

def show_sessions(userSessions):
    st.title("My Session History")
    st.sidebar.info("Select the session you want to view (Older to newer)")
    all_sessions = {session["session_id"] + " - " + session["session_type"] : i for i, session in enumerate(userSessions)}
    selSession = st.sidebar.radio("select a session", all_sessions.keys())
    if selSession:
        sessionInd = all_sessions[selSession]
        session = userSessions[sessionInd]
        st.subheader(f"Session -> {session['session_id']}")
        chats, count = chatActions.get_chat_from_db(uid = st.session_state["uid"], session_id=session["session_id"], rant=session["session_type"]=="Talk_session", getCount=True)
        display_session_chat(chats=chats, count=count)




def show_reports(all_r):
    st.title("My Reports")
    st.sidebar.info("Select the report you want to view (Older to newer)")
    all_reports = {session_id + " - " + report_details[0] : session_id for (session_id, report_details) in all_r.items()}
    selSession = st.sidebar.radio("select a session", all_reports.keys())
    if selSession:
        sessionId = all_reports[selSession]
        st.write(all_r[sessionId][1])


if 'uid' not in st.session_state:
    st.info("Please sign up/ login to continue")
else:
    if 'userSessions' not in st.session_state:
        st.session_state['userSessions'] = userActions.get_all_user_sessions(st.session_state["uid"])
    if 'all_r' not in st.session_state:
        st.session_state['all_r'] = userActions.get_user_reports(st.session_state["uid"])
    #st.title("My History")
    st.sidebar.title("Options")
    selection = st.sidebar.selectbox("Go to", ["Sessions", "Assessment Reports"])
    if selection == "Sessions":
        show_sessions(st.session_state['userSessions'])
    else:
        show_reports(st.session_state['all_r'])
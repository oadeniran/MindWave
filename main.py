import os
import random
import streamlit as st
from dotenv import load_dotenv
from core import mental_prediction, userActions
import uuid
import utils

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Setting the title of the app

def homepage():
    st.title('Hi, I am MindWave, and I am here to help you!')

    st.write("MindWave is here to help you understand your mental health better and give you tips on how you can improve.")

    st.write("Please select an option from the sidebar to get started.")

def auth():
    st.title('Authentication')
    st.write("Authenticatication enables me save your history and provide you with a better experience.")

    st.sidebar.title("Navigation")

    selection = st.sidebar.radio("Go to", ["SignIn", "SignUp"])

    if selection == "SignIn":
        st.info("Please enter your username and password to login.")
        email = st.text_input("Email")
        st.write("Please enter your password")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            resp = userActions.login({"email": email, "password": password})
            if resp["status_code"] == 200:
                st.success(resp["message"])
                st.session_state["uid"] = resp["uid"]
            else:
                st.error(resp["message"])
    elif selection == "SignUp":
        st.info("Please enter your details to sign up.")
        email = st.text_input("Email")
        st.write("Please enter your password")
        password = st.text_input("Password", type="password")
        if st.button("Sign Up"):
            resp = userActions.signup({"email": email, "password": password})
            if resp["status_code"] == 200:
                st.success(resp["message"])
            else:  
                st.error(resp["message"])

def test_configurations():
    st.title("Test Configurations")

    st.write("Please select the test configuration you want me to evaluate you on")

    test_option = st.selectbox("Test Options", ["Mental Health","Personality Test","Emotions Test"])

    verbosity = st.slider("Verbosity and Expressiveness", min_value=1, max_value=3, value=2)

    if st.button("Start Assesment"):
        if "uid" not in st.session_state:
            st.session_state["uid"] = ""
        st.session_state["test_option"] = test_option
        st.session_state["test_config"] = {
            "uid" : st.session_state["uid"],
            "session_id" : str(uuid.uuid4()),
            "test_option" : test_option,
            "verbosity" : verbosity,
            "input_info" : utils.get_input_format(test_option),
            "output_info" : utils.get_output_format(test_option)
        }
        st.info("Great!!! Let's get started")
        st.switch_page("pages/Assesment.py")





def about():
    pass


def main():
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ["Home Page","Authentication", "Test-configurations", "About page"])
    if selection == "Home Page":
        homepage()
    elif selection == "Authentication":
        auth()
    elif selection == "Test-configurations":
        test_configurations()
    elif selection == "About page":
        about()


if __name__ == "__main__":
    main()
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

    st.sidebar.title("Options")

    selection = st.sidebar.radio("Go to", ["SignIn", "SignUp"])

    if selection == "SignIn":
        st.info("Please enter your username and password to login.")
        email = st.text_input("Email", help="Please enter your email")
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
            resp = userActions.signup({"email": email, "password": password, "sessions": []})
            if resp["status_code"] == 200:
                st.success(resp["message"])
            else:  
                st.error(resp["message"])

def test_configurations():
    st.title("Test Configurations")

    st.write("Please select the test configuration you want me to evaluate you on")

    test_option = st.selectbox("Test Options", ["Mental Health","Personality Test"])

    verbosity = st.slider("Verbosity and Expressiveness", min_value=1, max_value=3, value=2)

    if st.button("Start Assesment"):
        if "uid" not in st.session_state:
            st.session_state["uid"] = ""
        st.session_state["test_option"] = test_option
        input_info = utils.get_input_format(test_option)
        output_info = utils.get_output_format(test_option)
        st.session_state["test_config"] = {
            "uid" : st.session_state["uid"],
            "session_id" : str(uuid.uuid4()),
            "test_option" : test_option,
            "verbosity" : verbosity,
            "input_info" : input_info,
            "output_info" : output_info,
            "system_template" : utils.get_system_template(test_option,output_info, input_info, verbosity)
        }
        userActions.add_user_session(st.session_state["uid"], st.session_state["test_config"]["session_id"], test_option,st.session_state["test_config"])
        st.info("Great!!! Let's get started")
        st.switch_page("pages/Assesment.py")





def about():
    about_str = """##Inspiration
The growing mental health crisis and the stigma associated with seeking help inspired us to create MindWave. We realized that many individuals avoid traditional mental health assessments because they feel too clinical or invasive. By leveraging Generative AI, we wanted to create a more engaging and comfortable way for people to share their mental health status, making it easier to detect potential issues early.

##What it does
MindWave offers users an interactive and conversational experience through GenAI. The AI engages users in meaningful conversations, gently collecting information that could indicate their mental health status. The data collected is processed using traditional machine learning models, which predict the user's mental state based on patterns and insights extracted from the interaction.

##How we built it
We combined the power of Generative AI with machine learning techniques. For the conversational aspect, we trained a custom model using various NLP techniques to make the interaction as natural and engaging as possible. The backend uses traditional ML models such as gradient boosting to analyze the gathered data and make mental health predictions. We also integrated secure data handling protocols to ensure user privacy and data protection.

##Challenges we ran into
One of the key challenges was ensuring that the AI could collect relevant data without sounding too invasive or clinical. Balancing sensitivity and accuracy in the machine learning models was another hurdle, as we had to fine-tune them to avoid overgeneralizing or underestimating the user's mental health status. Additionally, ensuring data privacy and securing sensitive information was paramount, which required extensive testing.

##Accomplishments that we're proud of
We’re proud of creating a solution that has the potential to democratize access to mental health assessments. MindWave engages users in a way that feels natural, reducing the discomfort often associated with mental health checks. Successfully integrating GenAI with traditional machine learning in this context was a significant achievement, as was building the platform with user privacy in mind.

##What we learned
We learned a lot about the intersection of AI and mental health. Developing this project deepened our understanding of how AI can be used responsibly to support mental well-being. We also gained insights into building conversational AI that maintains a balance between engagement and sensitivity, along with the complexities of data security in handling sensitive health information.

##What's next for MindWave
Moving forward, we plan to refine the AI’s conversational abilities, making it even more adept at detecting subtle mental health signals. We also aim to expand the mental health models to cover a broader range of mental health conditions. Additionally, we’re exploring partnerships with mental health professionals to validate our predictions and further improve the accuracy of the platform."""
    st.markdown(about_str)


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
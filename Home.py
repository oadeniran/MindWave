
import streamlit as st

@st.cache_resource
def get_all_imports():
    import os
    from dotenv import load_dotenv
    from core import userActions
    import uuid
    import utils
    import random
    return os, load_dotenv, userActions, uuid, utils, random

os, load_dotenv, userActions, uuid, utils, random = get_all_imports()

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Setting the title of the app

def homepage():
    st.title('Hi, I am MindWave, and I am here to help you!')

    st.write("MindWave is here to help you understand your mental health better and give you tips on how you can improve.")

    st.markdown("""
    ### Current Features:
    - **Personality Test** using the OCEAN model, providing insights into openness, conscientiousness, extraversion, agreeableness, and neuroticism.
    - **Mental Health Check** powered by traditional ML models trained with standard mental health datasets.
    - **Talk to Me** session, where users can discuss anything on their mind, including reflections on previous sessions.
                
    ### How to get started:
    #### 1. **Sign Up/ Login** to get started
    #### 2. **Select a Test Configuration** to evaluate yourself (You can start an assessment without authenticating but will not be able to save your history)
    #### 3. **Start Assesment** to begin the test
    #### 4. **View Results** to see your results
    #### 5. **Talk to Me** to discuss anything on your mind with MindWave (Only available after authentication)
    #### 6. **View History** to see your past sessions and reports (Only available after authentication)
     """)

    st.info("Please select an option from the sidebar to get started.")

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
                st.info("Loggin In....Wait for success message!")
                st.session_state["uid"] = resp["uid"]
                st.success(resp["message"])
                st.info("Now you can start your test configuration or talk to me")
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
                st.info("Signing Up....Wait for success message!")
                st.success(resp["message"])
                st.info("Now you can login with your details")
            else:  
                st.error(resp["message"])

def test_configurations():
    st.title("Test Configurations")

    st.write("Please select the test configuration you want me to evaluate you on")

    test_option = st.selectbox("Test Options", ["Personality Test", "Mental Health"])

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
    about_str = """
    ## Inspiration
    The growing mental health crisis and the stigma associated with seeking help inspired me to create MindWave. I realized that many individuals avoid traditional mental health assessments because they feel too clinical or invasive. By leveraging Generative AI, I wanted to create a more engaging and comfortable way for people to share their mental health status, making it easier to detect potential issues early.

    ## What it does
    MindWave offers users an interactive and conversational experience through GenAI. The AI engages users in meaningful conversations, gently collecting information that could indicate their mental health status. The data collected is processed using traditional machine learning models, which predict the user's mental state based on patterns and insights extracted from the interaction.

    ### Current Features:
    - **Personality Test** using the OCEAN model, providing insights into openness, conscientiousness, extraversion, agreeableness, and neuroticism.
    - **Mental Health Check** powered by traditional ML models trained with standard mental health datasets.
    - **Talk to Me** session, where users can discuss anything on their mind, including reflections on previous sessions.

    ## How I built it
    This MVP was built with Streamlit, MongoDB, MongoDB Atlas Vector with LangChain, LangChain, Scikit-Learn, and OpenAI.

    ### Mental Health Check
    Data was sourced from Kaggle and used to train multiple ML models, with the Random Forest model achieving the highest accuracy of 90%. This model was saved for prediction. For a more conversational data collection process, OpenAI and LangChain were used instead of a traditional form. The data collected is then formatted, and based on the model’s prediction, a report is generated.

    ### Personality Test
    For the personality test, I adopted the widely accepted OCEAN model. Using LangChain and OpenAI, I extract relevant user information to evaluate their traits on each dimension of the OCEAN model. Once collected, a personalized report is generated for the user.

    ### "Let's Talk" Session
    The "Let's Talk" session is powered by a Retrieval-Augmented Generation (RAG) implementation with MongoDB Atlas Vector Search. Here, previous session reports are stored as embeddings, giving the model context to refer back to user history. This allows users to freely discuss their feelings and ask about previous sessions, making the interaction more relevant and supportive.

    ### User History
    The user history feature enables users to review past reports and conversations, leveraging MongoDB document retrieval to store and present data from previous sessions.

    **Additionally, all user data, including authentication details and message history, is securely stored and managed in MongoDB.**

    ## Challenges Encountered
    One primary challenge involved ensuring that the AI could gather relevant data without appearing overly invasive or clinical. Balancing sensitivity and accuracy in the machine learning models required substantial fine-tuning to prevent both overgeneralization and underestimation of a user’s mental health indicators.

    Another significant challenge was managing user-specific embeddings to maintain unique, personalized interactions. This was fairly easy with Chroma DB as it allowed unique embeddings to be saved locally; however, MongoDB Atlas Vector Search works on an entire collection, making it difficult to isolate individual embeddings. An initial approach involved creating a separate collection per user, which would have allowed distinct embedding retrieval. However, MongoDB’s M0 cluster limitations (only four indexes per collection) constrained this approach.

    The final solution involved dynamically generating embeddings on each user interaction. For each session, historical reports for the user were used to create a vector store and retriever specific to that session. Once a response was provided, the user’s document was removed from the collection, and the vector store reset, ensuring that embeddings remained unique to each user and were efficiently retrievable. This approach allowed for personalized interactions within the capabilities of MongoDB Atlas Vector Search.

    ## Accomplishments that I'm proud of
    I'm proud of creating a solution that has the potential to democratize access to mental health assessments. MindWave engages users in a way that feels natural, reducing the discomfort often associated with mental health checks. Successfully integrating GenAI with traditional machine learning in this context was a significant achievement.
    
    Additionally, this was the very first time trying Atlas Vector Search, which proved to be a valuable experience, as ChromaDB had always been the preferred choice for embeddings previously, though MongoDB is my primary choice for databases.

    ## What I learned
    I learned a lot about the intersection of AI and mental health. Developing this project helped broaden my understanding of how AI can be used responsibly to support mental well-being. Insights were also gained into building conversational AI that maintains a balance between engagement and sensitivity.

    Additionally, I got to learn about Atlas Vector Search and its utility for storing embeddings and retrieving them in a conversational AI setting.

    ## What's next for MindWave
    Moving forward, there are plans to refine the AI’s conversational abilities, making it even more adept at detecting subtle mental health signals. Expanding the mental health models to cover a broader range of mental health conditions is also on the roadmap. Additionally, partnerships with mental health professionals are being explored to validate predictions and further improve the platform's accuracy.
    """
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
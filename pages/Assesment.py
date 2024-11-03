import streamlit as st

@st.cache_resource
def get_all_imports():
    import random
    from streamlit_chat import message
    import chatbot
    import utils
    from config import OPENAI_API_KEY
    return random, message, chatbot, utils, OPENAI_API_KEY

random, message, chatbot, utils, OPENAI_API_KEY = get_all_imports()



def MindWaveLab():
    output = None
    if 'test_config' not in st.session_state:
        st.info("Please select the test configuration you want me to evaluate you on")
    elif 'assessment_report' in st.session_state:
        st.info("Seems you have completed your assessment, please proceed to the assessment report. To start a new assessment, please click on the button below")
        if st.button("Start New Assessment"):
            st.session_state.clear()
            st.switch_page("Home.py")
    elif 'data_extracted' in st.session_state:
        st.success("Assessment Completed")
        st.write("Please click on the button below to generate your assessment report")
        if st.button("Generate Report"):
            st.spinner("Generating Report")
            st.info("Please wait for the success message while we generate your report")
            df_d = utils.convert_dict_to_df(st.session_state['data_extracted'])
            prediction = utils.get_prediction(st.session_state["test_config"]["test_option"], df_d)
            print("prediction===", prediction)
            report = chatbot.MindwaveReportBot(uid = st.session_state["test_config"]["uid"], session_id = st.session_state["test_config"]["session_id"], prediction = prediction, required_info = st.session_state["test_config"]["input_info"], curr_test=st.session_state["test_config"]["test_option"])
            st.session_state["assessment_report"] = report
            utils.add_report_to_db(st.session_state["test_config"]["uid"],st.session_state["test_config"]["test_option"], st.session_state["test_config"]["session_id"], report)
            st.success("Assessment Report Generated. Now Click in Assessment Result in sidebar to view results")
    else:
        if "past" not in st.session_state:
            #message("Hiiiiii!!, MindWave Here, Let's start shall we")
            st.session_state['past'] = []
        if "generated" not in st.session_state:
            st.session_state["generated"] = ["Hiiiiii!!, MindWave Here, Let's start shall we"]
        if "input_message_key" not in st.session_state:
            st.session_state["input_message_key"] = str(random.random())
        
        placeholder = st.empty()
        chat_container = placeholder.container()
        if st.session_state["generated"]:
            with chat_container:
                for i in range(len(st.session_state["generated"])):
                    if i > 1:
                        message(st.session_state["past"][i-2], is_user=True, key=str(i) + "_user")
                    message(st.session_state["generated"][i], key=str(i))

        if len(st.session_state['generated']) == 1:
            output = chatbot.MindWavebot(uid = st.session_state["test_config"]["uid"], session_id = st.session_state["test_config"]["session_id"], message = "", system_template=st.session_state["test_config"]["system_template"])
            st.session_state["generated"].append(output["message"])
            st.session_state["input_message_key"] = str(random.random())
            st.rerun()
        else:
            user_input = st.text_input("Type in your response", key=st.session_state["input_message_key"])
            if st.button("Send") and user_input != "":
                output = chatbot.MindWavebot(uid = st.session_state["test_config"]["uid"], session_id = st.session_state["test_config"]["session_id"], message = user_input, system_template=st.session_state["test_config"]["system_template"])
                st.session_state["past"].append(user_input)
                print("past", st.session_state["past"])
                st.session_state["generated"].append(output["message"])
                st.session_state["input_message_key"] = str(random.random())
            #st.rerun()
            #chat_container = st.container()
                if output["stages"] == "completed":
                    print("completed", output['dictionary_data'])
                    # Clean the chat container
                    st.session_state['data_extracted'] = output['dictionary_data'] 
                    st.rerun() 
                else:
                    st.rerun()



def assessment_report():
    if 'assessment_report' not in st.session_state:
        st.error("Please Finish your session in the MindWaveLab, to generate your report")
    else:
        st.title("Assessment Report")
        st.write("This is your assessment report")
        st.write(st.session_state['assessment_report'])



st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", ["MindWaveLab","Assesment Result"])
if selection == "MindWaveLab":
    MindWaveLab()
elif selection == "Assesment Result":
    assessment_report()
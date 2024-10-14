from langchain_core.messages import  HumanMessage
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
)
import re
import json
from openai import OpenAI
from datetime import datetime


from utils import dict_to_string, add_extracted_data_to_db, VERBOSITY_LEVEL
from core.chatActions import add_chat_to_db, get_chat_from_db
from config import OPENAI_API_KEY

def get_todays_date_formatted():
    return datetime.today().strftime('%Y-%m-%d')

LLM = ChatOpenAI(api_key=OPENAI_API_KEY, model_name="gpt-4o-mini", temperature=0.0)

def get_chat_history_for_ai(uid, session_id):
    chat_history = get_chat_from_db(uid, session_id)
    new_messages = []
    if not chat_history:
        return new_messages
    else:
        for message in chat_history:
            if message['type'] == 'human':
                temp_message = message['message']
                new_messages.append(HumanMessage(content=temp_message))
            else:
                # message = message['message']
                temp_message = message['message']
                new_messages.append(temp_message)

        return new_messages

def extract_dictionary_from_string(input_string):
    # Regular expression to find dictionary-like structure in the string
    dict_pattern = re.compile(r'\{.*?\}', re.DOTALL)
    
    # Search for the dictionary-like structure
    match = dict_pattern.search(input_string)
    
    if match:
        dict_string = match.group(0)
        
        # Attempt parsing the string to JSON
        dictionary = clean_and_parse_json(dict_string)
        return dictionary
    else:
        print("Error: No dictionary-like structure found in the input string.")
        return None

def clean_and_parse_json(input_string):
    # Step 1: Clean input by removing newline characters and excessive whitespace
    cleaned_string = re.sub(r'[\n\t]', '', input_string).strip()
    
    # Step 2: Convert single quotes to double quotes if needed
    cleaned_string = cleaned_string.replace("'", '"')
    
    # Step 3: Handle any trailing commas inside the dictionary
    cleaned_string = re.sub(r',(\s*[\}\]])', r'\1', cleaned_string)
    
    # Step 4: Try to parse the cleaned string into a JSON object
    try:
        dictionary = json.loads(cleaned_string)
        return dictionary
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None


def extract_stage_from_message(message):
    stage_pattern = re.compile(r'CURRENT_STAGE:\s*(\d+)', re.DOTALL)
    match = stage_pattern.search(message)
    if match:
        curr_stage = match.group(0)
        print("Current stage:", curr_stage)
        return curr_stage
    else:
        print("Error: No stage found in the input string.")
        return None

def remove_stage_from_message(message):
    pattern = r'CURRENT_STAGE:\s*\d+'

    # Replace the CURRENT_STAGE part with an empty string
    cleaned_message = re.sub(pattern, '', message)

    return cleaned_message

def MindWavebot(uid, session_id:str, message:str, output_format:str, required_info:str, verbosity=1):
    add_chat_to_db(uid, session_id, "user", message, {})
    output_format = f"""
      {output_format} 
        """
    
    required_info_s = required_info
  
    system_template = f"""

    You are a psychology expert and you are very good at evaluating the mental profile or psychological state of a person. Some information needs to be extracted and you can come up with scenarios and real world situsations where the user's response can be used to score the user for that information.
    You Love your job and you are very good at it. You are also a very very jovial person and you are good with words. A little information for you though, the current year is 2024 and today's date is {get_todays_date_formatted()}.
    You are to extract the following information from the user:

    {required_info_s}

    However, you do not want to explicitly ask the user for this information. You want to extract this information from the user's responses to your questions. You should ask questions that will help you deduce the information you need.
    
    When there is no user input, you should prompt the user for the information you need to extract.

    Your verbosity level is set to {verbosity} and that means you {VERBOSITY_LEVEL[verbosity]}.

    ON NO ACCOUNT SHOULD YOU LEAK YOUR GOAL OR MAKE ANY MENTION OF DICTIONARY OR JSON OR ANYTHING THAT WILL GIVE AWAY THE FACT THAT YOU ARE AN AI.

    While collecting information, end the message with excatly this text: CURRENT_STAGE: <Ind> where Ind is the index of the input being collected to indicate that you are currently collecting the information for that stage.

    When you have all the information ready, return the dictionary and DO NOT add any preambles or postambles or summary to the dictionary OUTPUT and Always output a dictionary in this format (field name as key and score as value) ONLY WHEN YOU HAVE ALL THE INFORMATION {output_format}.DO NOT add any preambles or postambles or summary to the dictionary OUTPUT. 
    
    As long as you can deduce that all information is collected from chat history, return the dictionary ONLY regardless of input from user.
    """

    sys_message = SystemMessagePromptTemplate.from_template(system_template)
    #print(sys_message)

    chat_prompts = ChatPromptTemplate.from_messages(
        [sys_message, MessagesPlaceholder("chat_history"), ("human", "{input}")]
    )

    print("Chat prompts:", chat_prompts)
    
    chain = chat_prompts | LLM
    
    session_chat_history = get_chat_history_for_ai(uid, session_id)

    model_response = chain.invoke(
            {"input": message, "chat_history": session_chat_history}
        )
    #print("Extracting dictionary from diana_response.content 1")
    dictionary_response = extract_dictionary_from_string(model_response.content)
    if not dictionary_response:
        print("Extracting dictionary from diana_response.content 2")
        dictionary_response = clean_and_parse_json(model_response.content)
    
    if dictionary_response:

        print("Extracted dictionary:", dictionary_response)
        
        add_chat_to_db(uid, session_id, "system", message,{"details_completed":True},)
        print("Added chat to DB with session_id:", session_id)
        add_extracted_data_to_db(uid, session_id, dictionary_response)
        return {
            "message": message,
            "type" : "system",
            "session_id": session_id,
            "stages" : "completed",
            "dictionary_data": dictionary_response
        }
    else:
        stages = extract_stage_from_message(model_response.content)
        # print("Extracted stages:", stages)
        print(1)
        print("Extracted stages:", stages)
        # print("Extracted stage:", stage)
        output = {}
        add_chat_to_db(uid, session_id, "system", model_response.content, output)
        output["message"] = remove_stage_from_message(model_response.content)
        output["session_id"] = session_id
        output["type"] = "system"
        output["stages"] = stages

        return output

def MindwaveReportBot(uid, session_id:str, prediction:str, required_info:str):
    output = {}
    
    required_info_s = required_info
  
    system_template = f"""

    You are a psychology expert and you are very good at evaluating the mental profile or psychological state of a person.

    The following information was collected from the user: {required_info_s}

    Based on this a ML model has predicted that the user is {prediction}.

    Generate an extensive report based on the information collected and the prediction made by the ML model. You have access to all the information collected from the user and you can use this information to generate the report.

    The report should be detailed and contain the following sections:
    1. Assessment Summary
    2. Detailed Predictions
    3. Behavioral Indicators
    4. Actionable Recommendations

    ON NO ACCOUNT SHOULD YOU LEAK YOUR GOAL OR MAKE ANY MENTION OF DICTIONARY OR JSON OR ANYTHING THAT WILL GIVE AWAY THE FACT THAT YOU ARE AN AI.
 
    """

    sys_message = SystemMessagePromptTemplate.from_template(system_template)
    #print(sys_message)

    chat_prompts = ChatPromptTemplate.from_messages(
        [sys_message, MessagesPlaceholder("chat_history")]
    )
    
    chain = chat_prompts | LLM
    
    session_chat_history = get_chat_history_for_ai(uid, session_id)

    model_response = chain.invoke(
            {"chat_history": session_chat_history}
        )
    
    return model_response.content
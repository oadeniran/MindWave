from db import usersCollection, messageCollection, extractedDataCollection
from datetime import datetime
from core import chatActions, mental_prediction
import pandas as pd

POSSIBLE_SELECTIONS = {
    "Mental Health": mental_prediction,
}

VERBOSITY_LEVEL = {
    1: "Direct and concise. Ask straightforward questions with minimal elaboration.",
    2: "Moderate verbosity. Ask questions with some detail and context, providing a bit of expressiveness and guidance.",
    3: "High verbosity and expressiveness. Present scenarios or hypothetical situations and ask questions about how the user would respond to these situations, using their responses to assess and score."
}

def dict_to_string(d, explanations=None):
    #i = 1
    result = []
    if explanations:
        for key, value in d.items():
            if isinstance(value, dict):
                value_str = ', '.join(f'{k}: {v}' for k, v in value.items())
                result.append(f'{key}: {explanations[key]}: value(numeric) can be {value_str}')
            elif isinstance(value, range):
                value_str = f'{value.start} to {value.stop - 1}'
                result.append(f'{key}: {explanations[key]}: score user with a numeric value between {value_str}')
            else:
                result.append(f'{key}: {value}')
        
        #i+=1
    else:
        for key, value in d.items():
            if isinstance(value, dict):
                value_str = ', '.join(f'{k}: {v}' for k, v in value.items())
                result.append(f'{key}: {value_str}')
            elif isinstance(value, range):
                value_str = f'{value.start} to {value.stop - 1}'
                result.append(f'{key}: {value_str}')
            else:
                result.append(f'{key}: {value}')
            
            #i+=1

    return '\n'.join(result)

def get_input_format(selection):
    d = POSSIBLE_SELECTIONS[selection].MAPPINGS
    explanations = POSSIBLE_SELECTIONS[selection].EXPLANATIONS
    return dict_to_string(d, explanations)

def get_output_format(selection):
    output_format = dict_to_string(POSSIBLE_SELECTIONS[selection].OUTPUT_FORMAT)
    return output_format

def convert_dict_to_df(d):
  df = pd.DataFrame(columns=d.keys())
  df.loc[0] = d.values()
  return df

def get_prediction(selection, data):
    return POSSIBLE_SELECTIONS[selection].get_prediction(data)

def add_extracted_data_to_db(uid, session_id:str, data:dict):
    document = {
        "uid":uid,
        "session_id":session_id,
        "data":data,
        "date":datetime.now(),
    }
    extractedDataCollection.insert_one(document)

def add_report_to_db(uid, session_id:str, report:str):
    document = {
        "uid":uid,
        "session_id":session_id,
        "report":report,
        "date":datetime.now(),
    }
    extractedDataCollection.insert_one(document)


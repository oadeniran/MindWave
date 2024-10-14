from db import messageCollection
from datetime import datetime
    
def add_chat_to_db(uid, session_id:str,type:str,message:str, extra_info:dict):
    document = {
        "uid":uid,
        "session_id":session_id,
        "type":type,
        "message":message,
        "date":datetime.now(),
    }
    if extra_info:
        document.update(extra_info)
    messageCollection.insert_one(document)
    
def get_chat_from_db(uid, session_id):
    try:
        chats = messageCollection.find({"uid":uid, "session_id": session_id})
        return chats
    except Exception as e:
        print(e)
        return "Error with chat retrieval"
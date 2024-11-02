from db import usersCollection, reportsCollection
import json
from bson import ObjectId
    
def signup(signUp_det):
    try:
        details = usersCollection.find_one({"email" : signUp_det["email"]})
    except:
        return {
                    "message" : "Error in signup, please try again",
                    "status_code" : 404
                    }
    if details:
        return {
                    "message" : "Username is taken, please use another",
                    "status_code" : 400}
    try:
        usersCollection.insert_one(signUp_det)
    except:
        return {
                    "message" : "Error with signup",
                    "status_code" : 400}
    return {
    "message" : "Sign Up successful",
    "status_code" : 200}

def login(login_det):

    try:
        details = usersCollection.find_one({"email" : login_det["email"]})
    except:
        return {
                    "message" : "Error with DB",
                    "status_code" : 404
                    }
    
    if details:
        print(str(details["_id"]))
        if details["password"] == login_det["password"]:
            return {
                    "message" : "Sign In successful",
                    "status_code" : 200,
                    "uid" : str(details["_id"])}
        else:
            return {
            "message" : "Wrong Password",
            "status_code" : 400}
    else:
        return {
                    "message" : "User not found",
                    "status_code" : 404
                    }

def add_user_session(uid, session_id, session_type, session_info):
    try:
        usersCollection.update_one({"_id":ObjectId(uid)}, {"$push": {"sessions": {"session_id": session_id, "session_type": session_type, "session_info": session_info}}})
    except:
        return {
                    "message" : "Error with DB",
                    "status_code" : 404
                    }
    return {
    "message" : "Session added successfully",
    "status_code" : 200}

def get_all_user_sessions(uid):
    try:
        print(uid)
        users = usersCollection.find({"_id":ObjectId(uid)})
    except:
        return {
                    "message" : "Error with DB",
                    "status_code" : 404
                    }
    #print(list(users))
    return list(users)[0]["sessions"]

def add_doc_ids(uid, ids):
    try:
        print(uid)
        user = usersCollection.find({"_id":ObjectId(uid)})
    except:
        return {
                    "message" : "Error with DB",
                    "status_code" : 404
                    }
    #print(list(users))
    new_ids = user["docIds"] + ids
    user["docIds"] = new_ids

    try:
        usersCollection.find_one_and_update({"_id":ObjectId(uid)}, {"docIds" : new_ids})
    except:
        return {
                    "message" : "Error with DB",
                    "status_code" : 404
                    }
    return "updated"

def get_user_reports(uid):
    try:
        reports = reportsCollection.find({"uid":uid})
    except:
        return {
                    "message" : "Error with DB",
                    "status_code" : 404
                    }
    reports_formatted = {report['session_id']: (report['session_type'], report['report'], report["saved"]) for report in reports}
    #print(reports_formatted)
    return reports_formatted
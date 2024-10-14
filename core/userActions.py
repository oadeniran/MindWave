from db import usersCollection
import json

    
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
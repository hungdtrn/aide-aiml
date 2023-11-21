import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

import json
from flask import Flask, jsonify, request, render_template, Response

import storage
import datetime
from ai.chatsession import ChatSession
from ai import VERSION

app = Flask(__name__)
sessionDict = {}

def _get_today():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def _get_now():
    return datetime.datetime.now().isoformat()

def get_session_or_create(userId):
    if userId in sessionDict:
        return sessionDict[userId]
    else:
        conversations = storage.readConversation(userId)
        carerInput = storage.readCarerInput(userId)
        medicalInput = storage.readMedicalInput(userId)
        sessionDict[userId] = ChatSession(conversations=conversations,
                                          carerInput=carerInput,
                                          medicalInput=medicalInput)
        return sessionDict[userId]

@app.route('/')
def test():
    return "Success"

@app.route('/createUser', methods=['POST'])
def createUser():
    userId = request.json["userId"]
    storage.writeUser(userId, request.json)
    
    sessionDict[userId] = {
        "history": [],
    }
    return json.dumps({"userId": request.json["userId"]})

@app.route("/welcome", methods=['GET'])
def welcome():
    """ Get the welcome message from the server
    """
    userId = request.json["userId"]
    session = get_session_or_create(userId)
    conversations = storage.readConversation(userId)
    if not conversations or conversations[-1]["date"] != _get_today():
        conversations.append({
            "date": _get_today(),
            "conversation": [],
            "version": VERSION,
            "tokeCnt": 0,
        })

    response = session.welcome()
    conversations[-1]["conversation"].append({
        "time": _get_now(),
        session.ai_prefix: response,
        "tokenCnt": 0,
    })
    storage.writeConversation(userId, conversations)

    return {
        "response": response
    }

@app.route("/chat", methods=['POST'])
def chat():
    """ Chat with ChatGPT
    """
    userId = request.json["userId"]
    session = get_session_or_create(userId)

    conversations = storage.readConversation(userId)
    if not conversations or conversations[-1]["date"] != _get_today():
        conversations.append({
            "date": _get_today(),
            "conversation": [],
            "version": VERSION,
            "tokeCnt": 0,
        })

    message = request.json["message"]
    conversations[-1]["conversation"].append({
        "time": _get_now(),
        session.human_prefix: message,
        "tokenCnt": 0,
    })

    response = session.chat(message)
    conversations[-1]["conversation"].append({
        "time": _get_now(),
        session.ai_prefix: response,
        "tokenCnt": 0,
    })

    storage.writeConversation(userId, conversations)

    return {
        "response": response
    }

@app.route("/chat_stream", methods=['POST'])
def chat_stream():
    """ Chat with ChatGPT, but streaming tokens
    """
    userId = request.json["userId"]
    session = get_session_or_create(userId)
    message = request.json["message"]

    conversations = storage.readConversation(userId)
    if not conversations or conversations[-1]["date"] != _get_today():
        conversations.append({
            "date": _get_today(),
            "conversation": [],
            "version": VERSION,
            "tokeCnt": 0,
        })

    conversations[-1]["conversation"].append({
        "time": _get_now(),
        session.human_prefix: message,
        "tokenCnt": 0,
    })

    response_gen = session.chat(message, streaming=True)
    def generate():
        msg = ""
        for word in response_gen:
            msg += word
            yield word
        msg.strip()
        conversations[-1]["conversation"].append({
            "time": _get_now(),
            session.ai_prefix: msg,
            "tokenCnt": 0,
        })
        storage.writeConversation(userId, conversations)
        yield ""

    response = app.response_class(generate(), mimetype='text/text')
    return response

@app.route("/dailySummary", methods=['GET'])
def getDailySummary():
    """ Get the summary of today and the past n-1 days
    """
    userId = request.json["userId"]
    dailySummary = storage.readDailySummary(userId)
    num_summary = request.json["n"]
    if not dailySummary or dailySummary[-1]["date"] != _get_today():
        # Get today's conversation
        conversations = storage.readConversation(userId)
        if not conversations or conversations[-1]["date"] != _get_today():
            # Skip the summary if we don't have any conversation data for today!
            pass
        else:
            session = get_session_or_create(userId)
            currentDailySummary = session.dailySummary(conversations[-1]["conversation"])
            dailySummary.append({
                "date": _get_today(),
                "summary": currentDailySummary,
                "tokenCnt": 0,
                "aiVersion": VERSION,
            })
            storage.writeDailySummary(userId, dailySummary)
        
    return {
        "response": dailySummary[-num_summary:]
    }


@app.route("/devSummary", methods=['GET'])
def getdevSummary():
    userId = request.json["userId"]
    devSummary = storage.readDevSummary(userId)
    num_summary = request.json["n"]
    if not devSummary or devSummary[-1]["date"] != _get_today():
        # Get today's conversation
        conversations = storage.readConversation(userId)
        currentConv = conversations[-1]["conversation"]
        if not conversations or conversations[-1]["date"] != _get_today():
            # Skip the summary if we don't have any conversation data for today!
            pass
        else:
            session = get_session_or_create(userId)
            

            # Get past summary
            pastSumm = ""
            if devSummary:
                pastSumm = devSummary[-1]["summary"]

            # Update the development summary
            currentdevSummary = session.devSummary(pastSumm, currentConv)

            devSummary.append({
                "date": _get_today(),
                "summary": currentdevSummary,
                "tokenCnt": 0,
                "aiVersion": VERSION,
            })
            storage.writeDevSummary(userId, devSummary)
    
    return {
        "response": devSummary[-num_summary:]
    }

@app.route("/healthRecord", methods=['GET'])
def getHealthRecord():
    userId = request.json["userId"]
    healthRecord = storage.readHealthRecord(userId)
    num_record = request.json["n"]
    if not healthRecord or healthRecord[-1]["date"] != _get_today():
        session = get_session_or_create(userId)
        currentHealthRecord = session.healthRecord()
        healthRecord.append(currentHealthRecord)
        storage.writeHealthRecord(userId, healthRecord)
    
    currentHealthRecord = healthRecord[-num_record:]
    return {
        "response": currentHealthRecord
    }

@app.route("/medicalInput", methods=['GET'])
def getMedicalInput():
    userId = request.json["userId"]
    medicalInput = storage.readMedicalInput(userId)    
    currentMedicalInput = medicalInput[-1]
    return {
        "response": currentMedicalInput
    }

@app.route("/carerInput", methods=['GET'])
def getCarerInput():
    userId = request.json["userId"]
    carerInput = storage.readCarerInput(userId)    
    currentCarerInput = carerInput[-1]
    return {
        "response": currentCarerInput
    }

@app.route("/medicalInput", methods=['POST'])
def updateMedicalInput():
    pass

@app.route("/carerInput", methods=['POST'])
def updateCarerInput():
    pass

if __name__ == "__main__":
    "Create dummy data"
    import shutil
    if not os.path.exists(storage.STORAGE_PATH):
        os.mkdir(storage.STORAGE_PATH)
    for folderName in os.listdir(storage.DUMMY_PATH):
        if not os.path.exists(os.path.join(storage.STORAGE_PATH, folderName)):
            shutil.copytree(os.path.join(storage.DUMMY_PATH, folderName), os.path.join(storage.STORAGE_PATH, folderName))
    

    app.run(host='0.0.0.0', debug="True", port=8080)

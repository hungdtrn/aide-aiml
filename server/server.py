import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

import json
from flask import Flask, jsonify, request, render_template

import storage
from ai.chatsession import ChatSession

app = Flask(__name__)
sessionDict = {}

def get_session_or_create(userId):
    if userId in sessionDict:
        return sessionDict[userId]
    else:
        history = storage.readHistory(userId)
        sessionDict[userId] = ChatSession(history=history)
        return sessionDict[userId]

@app.route('/')
def test():
    return "Success"

@app.route('/createUser', methods=['POST'])
def createUser():
    userId = request.json["userId"]
    storage.writeUser(userId, request.json)
    storage.writeHistory(userId, [])
    sessionDict[userId] = {
        "history": [],
    }
    return json.dumps({"userId": request.json["userId"]})

@app.route("/welcome", methods=['POST'])
def welcome():
    userId = request.json["userId"]
    session = get_session_or_create(userId)
    return {
        "msg": session.welcome()
    }
    
@app.route("/chat", methods=['POST'])
def chat():
    userId = request.json["userId"]
    message = request.json["message"]
    session = get_session_or_create(userId)
    return {
        "msg": session.chat(message)
    }

@app.route("/summary", methods=['POST'])
def summary():
    userId = request.json["userId"]
    session = get_session_or_create(userId)
    history = session.summary()
    storage.writeHistory(userId, history)
    return {
        "history": history
    }

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug="True", port=8080)

import os
import json
from flask import Flask, jsonify, request, render_template

import storage

app = Flask(__name__)
sessionDict = {}

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
    history = storage.readHistory(userId)
    sessionDict[userId] = {
        "history": history
    }
    if history:
        msg = "Welcome back!"
    else:
        msg = "Hello! It's great to know you!"

    return {
        "msg": msg
    }
    
@app.route("/chat", methods=['POST'])
def chat():
    userId = request.json["userId"]
    message = request.json["message"]
    session = sessionDict[userId]
    return {"msg": "sever response\: {}".format(message)}



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug="True", port=8080)

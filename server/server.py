import os
import json
from flask import Flask, jsonify, request, render_template

import storage

app = Flask(__name__)

@app.route('/')
def test():
    return "Success"

@app.route('/createUser', methods=['POST'])
def createUser():
    storage.writeUser(request.json["userId"], request.json)
    return json.dumps({"userId": request.json["userId"]})


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug="True", port=8080)

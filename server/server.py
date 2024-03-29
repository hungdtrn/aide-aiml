import os
import sys
import shutil
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

import json
from flask import Flask, jsonify, request, render_template, Response

import storage
from send_email import send_email_notification
from utils import get_now, get_today, insights_from_description, get_conversations, process_data_for_demo, prepare_topic
from ai import VERSION, MODELS, build_chat_session, build_summariser, build_chat_retriever

AI_MODEL = MODELS.CHATGPT


print("---------- For the first time: Initialise data --------")
if not os.path.exists(storage.STORAGE_PATH):
    os.mkdir(storage.STORAGE_PATH)
for folderName in os.listdir(storage.MOCKDATA_PATH):
    if not os.path.exists(os.path.join(storage.STORAGE_PATH, folderName)):
        print("Coping folder", folderName)
        shutil.copytree(os.path.join(storage.MOCKDATA_PATH, folderName), os.path.join(storage.STORAGE_PATH, folderName))


print("----------- Preparing and Processing the data. This may take while --------")
process_data_for_demo()
print("----------- Loading previous conversations into long-term memory for information retrieval")
print("----------- Loading for the demo user -------")
retrievers = {
    0: build_chat_retriever(storage.readConversation(0)),
}

app = Flask(__name__)

chatSessionDict = {}

def _get_chatsession_or_create(userId, uiType="streamlit"):
    if userId in chatSessionDict:
        return chatSessionDict[userId]
    else:
        conversations = storage.readConversation(userId)
        patient_description = insights_from_description(userId)
        topics = prepare_topic(userId, get_today(), cached=True)

        if userId not in retrievers:
            retrievers[userId] = build_chat_retriever(conversations)

        chatSessionDict[userId] = build_chat_session(AI_MODEL,
                                                     retriever=retrievers[userId],
                                                     conversations=conversations,
                                                     patient_info=patient_description,
                                                     topics=topics,
                                                     device=uiType)
        
        return chatSessionDict[userId]
    

def _userDailySummary(userId):
    dailySummary = storage.readDailySummary(userId)
    num_summary = request.json["n"]
    if not dailySummary or dailySummary[-1]["date"] != get_today():
        # Get today's conversation
        conversations = storage.readConversation(userId)
        if not conversations or conversations[-1]["date"] != get_today():
            # Skip the summary if we don't have any conversation data for today!
            pass
        else:
            summariser = build_summariser(AI_MODEL)
            currentDailySummary = summariser.dailySummary(conversations[-1])
            dailySummary.append({
                "date": get_today(),
                "summary": currentDailySummary,
                "tokenCnt": 0,
                "aiVersion": VERSION,
            })
            storage.writeDailySummary(userId, dailySummary)

    return {
        "response": dailySummary[-num_summary:]
    }

@app.route('/')
def test():
    return "Success"

@app.route('/createUser', methods=['POST'])
def createUser():
    userId = request.json["userId"]
    storage.writeUser(userId, request.json)

    chatSessionDict[userId] = {
        "history": [],
    }
    return json.dumps({"userId": request.json["userId"]})

@app.route("/welcome", methods=['POST'])
def welcome():
    def _save_welcome(conversation, welcome):
        "avoid saving multiple conversation"
        if not conversation["conversation"] or "human" in conversation["conversation"][-1]["content"]:
            conversation["conversation"].append({
                "time": get_now(),
                "content": {session.ai_prefix: welcome,},
                "tokenCnt": 0,
            })
        else:
            conversation["conversation"][-1] = {
                "time": get_now(),
                "content": {session.ai_prefix: welcome,},
                "tokenCnt": 0,
            }

        return conversation

    """ Get the welcome message from the server
    """
    userId = request.json["userId"]
    uiType = request.json.get("uiType", "streamlit")

    streaming = request.json.get("streaming", False)

    session = _get_chatsession_or_create(userId, uiType)
    conversations = get_conversations(userId)
    session.reload_memory(conversations)

    response = session.welcome(streaming=streaming)
    if not streaming:
        conversations[-1] = _save_welcome(conversations[-1], response)
        storage.writeConversation(userId, conversations)
        return {
            "response": response
        }
    else:
        def generate():
            msg = ""
            for word in response:
                msg += word
                yield word
            msg.strip()
            conversations[-1] = _save_welcome(conversations[-1], msg)
            storage.writeConversation(userId, conversations)
            yield ""

        return app.response_class(generate(), mimetype='text/text')

@app.route("/chat", methods=['POST'])
def chat():
    """ Chat with the language model
    """
    streaming = request.json.get("streaming", False)
    uiType = request.json.get("uiType", "streamlit")

    # Get the chat session
    userId = request.json["userId"]
    session = _get_chatsession_or_create(userId, uiType)
    message = request.json["message"]

    # Get the conversation history
    conversations = get_conversations(userId)

    # Store the message of the human
    conversations[-1]["conversation"].append({
        "time": get_now(),
        "content": {session.human_prefix: message,},
        "tokenCnt": 0,
    })

    # Get the details AI extracted from the carer and medical inputs
    userDetails = insights_from_description(userId)

    if streaming:
        response_gen = session.chat(message, streaming=True)
        def generate():
            msg = ""
            is_finished = True


            for (word, response) in response_gen:
                msg += word
                yield word
            msg.strip()

            for info in response.generations:
                gen_info = info[0].generation_info
                is_finished = is_finished & (gen_info["finish_reason"] == "stop")

            if not is_finished:
                print("Trying to continue the response")
                continue_response_gen = session.chat("Please continue", streaming=True)
                for (word, response) in continue_response_gen:
                    msg += word
                    yield word
                msg.strip()

            conversations[-1]["conversation"].append({
                "time": get_now(),
                "content": {session.ai_prefix: msg,},
                "tokenCnt": 0,
                "is_finished": is_finished,
                "gen_info": gen_info,
            })
            storage.writeConversation(userId, conversations)
            yield ""

        response = app.response_class(generate(), mimetype='text/text')
        return response
    else:
        response = session.chat(message, streaming=False)
        conversations[-1]["conversation"].append({
            "time": get_now(),
            "content": {session.ai_prefix: response,},
            "tokenCnt": 0,
        })

        storage.writeConversation(userId, conversations)

        return {
            "response": response
        }


@app.route("/chat_history", methods=["POST"])
def chat_history():
    # Get the chat session
    userId = request.json["userId"]
    date = request.json["date"]
    conversations = get_conversations(userId)
    conv = []
    for conversation in conversations:
        if conversation["date"] == date:
            conv = conversation["conversation"]
            break

    return {
        "response": conv
    }

@app.route("/scheduledDailySummary", methods=['GET'])
def scheduledDailySummary():
    """ Invoked by Daily CRON scheduler
        Get the summary of today and the past n-1 days for all users
    """
    for userId in storage.yesterdaysUsers():
        summary = _userDailySummary(userId)
        user = storage.readUser(userId)
        indicator = storage.readIndicator(userId)

        if false: # Disable email sending
            if indicator.mental_heath < 0:
                send_email_notification(user, "Mental health has steadily declined")
            if indicator.physical_heath < 0:
                send_email_notification(user, "Physical health has steadily declined")
            if indicator.social_heath < 0:
                send_email_notification(user, "Social health has steadily declined")

    return "Success"

@app.route("/dailySummary", methods=['POST'])
def getDailySummary():
    """ Get the summary of today and the past n-1 days
    """
    userId = request.json["userId"]
    return _userDailySummary(userId)

@app.route("/devSummary", methods=['POST'])
def getdevSummary():
    userId = request.json["userId"]
    devSummary = storage.readDevSummary(userId)
    num_summary = request.json["n"]

    if not devSummary or devSummary[-1]["date"] != get_today():
        # Get today's conversation
        conversations = storage.readConversation(userId)
        currentConv = conversations[-1]["conversation"]
        if not conversations or conversations[-1]["date"] != get_today():
            # Skip the summary if we don't have any conversation data for today!
            pass
        else:
            summariser = build_summariser(AI_MODEL)

            # Get past summary
            pastSumm = ""
            if devSummary:
                pastSumm = devSummary[-1]["summary"]

            # Update the development summary
            currentdevSummary = summariser.devSummary(pastSumm, currentConv)

            devSummary.append({
                "date": get_today(),
                "summary": currentdevSummary,
                "tokenCnt": 0,
                "aiVersion": VERSION,
            })
            storage.writeDevSummary(userId, devSummary)

    return {
        "response": devSummary[-num_summary:]
    }

@app.route("/indicator", methods=['POST'])
def getIndicator():
    userId = request.json["userId"]
    indicators = storage.readIndicator(userId)
    dailySummaries = _userDailySummary(userId)["response"]
    summariser = build_summariser(AI_MODEL)
    indicator_by_date = {}
    cached = True
    for s in indicators:
        indicator_by_date[s["date"]] = s
    
    out = []
    for i, s in enumerate(dailySummaries):
        current_date = s["date"]
        if current_date in indicator_by_date and indicator_by_date[current_date].get("indicators", "") and cached:
            out.append(indicator_by_date[current_date])
            continue

        if not s["summary"]:
            out.append({
                "date": current_date,
                "indicators": {},
                "aiVersion": VERSION,
            })
            continue

        currentIndicator = summariser.computeIndicators(s["summary"])
        out.append({
                "date": current_date,
                "indicators": currentIndicator,
                "aiVersion": VERSION,
        })

    storage.writeIndicator(userId, out)

    return {
        "response": out
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

def preriodicSaveSummary():
    "TODO: Periodically get the daily, the development summary and save it to the server at the end of each day"
    pass

if __name__ == "__main__":
    "Create dummy data"


    app.run(host='0.0.0.0', debug="True", port=8080)

import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

import datetime
import storage
import numpy as np

from ai import VERSION, MODELS, build_chat_session, build_summariser, build_conversation_prompter
AI_MODEL = MODELS.CHATGPT

def get_today():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def get_now():
    return datetime.datetime.now().isoformat()

def insights_from_description(userId):
    user = storage.readUser(userId)
    if not user:
        user = {"userId": userId, 
                "ai_details": []}
        
    carerInputs = storage.readCarerInput(userId)
    if not carerInputs:
        carerInputs = [{
            "id": 0,
            "createdAt": get_now(),
            "doctorId": 0,
            "details": "No details yet"
        }]
        storage.writeCarerInput(userId, carerInputs)

    medicalInputs = storage.readMedicalInput(userId)
    if not medicalInputs:
        medicalInputs = [{
            "id": 0,
            "createdAt": get_now(),
            "doctorId": 0,
            "details": "No details yet"
        }]
        storage.writeMedicalInput(userId, medicalInputs)

    lastCarerInput, lastMedicalInput = carerInputs[-1], medicalInputs[-1]
    if not user.get("ai_details", []) or user["ai_details"][-1]["id"] != [lastCarerInput["id"], lastMedicalInput["id"]]:
        conversation_prompter = build_conversation_prompter(AI_MODEL)
        newDetails = {
            "id": (lastCarerInput["id"], lastMedicalInput["id"]),
            "details": conversation_prompter.insights_from_description(lastCarerInput["details"], lastMedicalInput["details"]),
        }
        if not user.get("ai_details", []):
            user["ai_details"] = [newDetails]
        else:
            user["ai_details"].append(newDetails)
        storage.updateUser(userId, user)
    
    return user["ai_details"]

def get_today_conversation(userId):
    conversations = storage.readConversation(userId)
    if len(conversations)==0 or conversations[-1]["date"] != get_today():
        conversations.append({
            "date": get_today(),
            "conversation": [],
            "version": VERSION,
            "tokeCnt": 0,
        })
    return conversations


# def get_details_from_last_conversation(conversations):
#     if len(conversations) <= 1:
#         return []

#     conversation = conversations[-2]
#     conversation_prompter = build_conversation_prompter(AI_MODEL)
#     return conversation_prompter.extractFromConversation(conversation)

def _insights_from_description(conversation):
    conversation_prompter = build_conversation_prompter(AI_MODEL)
    information = conversation_prompter.insights_from_conversation(conversation)
    return information

def insights_from_conversation(conversation_dict, cached=True):
    if conversation_dict["information"] and cached:
        print("Using cached information")
        return conversation_dict

    conversation_dict["information"] = _insights_from_description(conversation_dict["conversation"])
    return conversation_dict

def prepare_topic(userId, date, cached=True):
    """ Preparing the topic for the next conversations and save it to the database

    This involves multiple steps:
    1. Get the last n_prev_conv conversations
    2. Get n_random_conv random conversations from the past
    3. Get the extracted information from these conversations
    4. Generate the topic suggestions
    5. Save the topic suggestions to the database
    
    OPTIONALS:
    6. Query the relevant contexts for each topics
    """
    n_prev_conv = 1
    n_random_conv = 1

    raw_conversations = storage.readConversation(userId)
    if len(raw_conversations) == 0:
        return []
    
    # Onlu considers the dates with conversations
    conversations = [x for x in raw_conversations if x["conversation"]]

    # If last conversation is empty, use the suggestions from that conversation
    if not conversations[-1]["conversation"] and conversations[-1].get("topicSuggestions", []):
        pass

    # prepare the previous conversations
    last_conv = conversations[-n_prev_conv:]

    # prepare the remain conversation
    remains = len(conversations) - n_prev_conv
    if remains > 0:
        if remains > n_random_conv:
            random_conv = np.random.choice(conversations[:remains], n_random_conv, replace=False)
        else:
            random_conv = conversations[:remains]
    else:
        random_conv = []

    next_conv = {
        "date": date,
        "conversation": [],
        "version": VERSION,
        "tokeCnt": 0,
        "topicSuggestions": [], "information": []
    }
    is_new = True

    for i in range(len(conversations)):
        if conversations[i]["date"] == date:
            last_conv = conversations[i-n_prev_conv:i]
            next_conv = conversations[i]
            remains = i - n_prev_conv
            if remains > 0:
                if remains > n_random_conv:
                    random_conv = np.random.choice(conversations[:remains], n_random_conv, replace=False)
                else:
                    random_conv = conversations[:remains]
            else:
                random_conv = []

            is_new = False
            break
        elif conversations[i]["date"] > date:
            print("No date specified")
            return

    if cached and next_conv["topicSuggestions"]:
        print("Using cached topic suggestions")
        return next_conv["topicSuggestions"]

    convs = [insights_from_conversation(conversation) for conversation in random_conv]
    convs.extend([insights_from_conversation(conversation) for conversation in last_conv])

    storage.writeConversation(userId, raw_conversations)

    patient_info = insights_from_description(userId)
    conversation_prompter = build_conversation_prompter(AI_MODEL)
    conversation_prompter.topic_suggestions(patient_info, convs)


    

    # conversation = conversations[-2]
    # summariser = build_summariser(AI_MODEL)
    # return summariser.summarise(conversation)

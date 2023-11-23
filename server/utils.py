import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

import datetime
import storage
import numpy as np
import time
from ai import VERSION, MODELS, build_chat_session, build_summariser, build_conversation_prompter, get_today, get_now
AI_MODEL = MODELS.CHATGPT


def insights_from_description(userId, conversation_prompter=None):
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
        if not conversation_prompter:
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
    
    return user["ai_details"][-1]["details"][0]

def get_conversations(userId):
    conversations = storage.readConversation(userId)
    if len(conversations)==0 or conversations[-1]["date"] != get_today():
        conversations.append({
            "date": get_today(),
            "conversation": [],
            "version": VERSION,
            "tokeCnt": 0,
        })
    return conversations

def save_summary(userId):
    pass

# def get_details_from_last_conversation(conversations):
#     if len(conversations) <= 1:
#         return []

#     conversation = conversations[-2]
#     conversation_prompter = build_conversation_prompter(AI_MODEL)
#     return conversation_prompter.extractFromConversation(conversation)

def _insights_from_description(conversation, conversation_prompter=None):
    if not conversation_prompter:
        conversation_prompter = build_conversation_prompter(AI_MODEL)
    
    information = conversation_prompter.insights_from_conversation(conversation)
    return information

def insights_from_conversation(conversation_dict, cached=True, conversation_prompter=None):
    if conversation_dict.get("information", []) and cached:
        print("Using cached information")
        return conversation_dict

    conversation_dict["information"] = _insights_from_description(conversation_dict, conversation_prompter)
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
        return ""
    
    if raw_conversations[-1]["date"] == date and raw_conversations[-1].get("topicSuggestions", []):
        print("Using cached topic suggestions")
        return raw_conversations[-1]["topicSuggestions"]

    
    # If last conversation is empty, use the suggestions from that conversation
    if not raw_conversations[-1]["conversation"] and raw_conversations[-1]["date"] < date and raw_conversations[-1].get("topicSuggestions", []):
        raw_conversations.append({
            "date": date,
            "conversation": [],
            "version": VERSION,
            "tokeCnt": 0,
            "topicSuggestions": raw_conversations[-1].get("topicSuggestions"),
            "information": []
        })
        storage.writeConversation(userId, raw_conversations)
        return raw_conversations[-1].get("topicSuggestions")


    # Only considers the dates with conversations
    conversations = [x for x in raw_conversations if x["conversation"]]


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
        "topicSuggestions": [], 
        "information": []
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
            return ""

    if cached and next_conv.get("topicSuggestions", []):
        print("Using cached topic suggestions")
        return next_conv["topicSuggestions"]

    conversation_prompter = build_conversation_prompter(AI_MODEL)
    print("----- Extracting insights from previous conversations -------")
    convs = [insights_from_conversation(conversation, conversation_prompter=conversation_prompter) for conversation in random_conv]
    convs.extend([insights_from_conversation(conversation, conversation_prompter=conversation_prompter) for conversation in last_conv])

    storage.writeConversation(userId, raw_conversations)

    patient_info = insights_from_description(userId, conversation_prompter=conversation_prompter)

    print("------- Thinking of the topics ---------")
    suggested_topics = conversation_prompter.topic_suggestions(patient_info, convs)
    next_conv["topicSuggestions"] = suggested_topics
    if is_new:
        raw_conversations.append(next_conv)
    
    storage.writeConversation(userId, raw_conversations)
    
    return next_conv["topicSuggestions"]

    

    # conversation = conversations[-2]
    # summariser = build_summariser(AI_MODEL)
    # return summariser.summarise(conversation)


def _summarize_all_previous_conversation(userId, cached=True):
    """ For demo. Summarise all previous conversations
    """

    conversations = storage.readConversation(userId)
    summary_list = storage.readDailySummary(userId)
    summariser = build_summariser(AI_MODEL)
    summaries_by_date = {}
    for s in summary_list:
        summaries_by_date[s["date"]] = s

    out = []

    for i, conv in enumerate(conversations):
        current_date = conv["date"]
        if current_date in summaries_by_date and summaries_by_date[conv["date"]].get("summary", "") and cached:
            print("Using previous summary")
            out.append(summaries_by_date[current_date])
            continue

        if current_date == get_today():
            break

        if not conv["conversation"]:
            out.append({
                "date": current_date,
                "summary": "",
                "tokenCnt": 0,
                "aiVersion": VERSION,
            })
            continue         
       

        print("Summarising {}".format(current_date))
        currentDailySummary = summariser.dailySummary(conv)
        out.append({
                "date": current_date,
                "summary": currentDailySummary,
                "tokenCnt": 0,
                "aiVersion": VERSION,
        })
    
    storage.writeDailySummary(userId, out)
    
def _compute_indicator_all_previous_conversation(userId, cached=True):
    dailySummaires = storage.readDailySummary(userId)
    indicators = storage.readIndicator(userId)
    summariser = build_summariser(AI_MODEL)
    indicator_by_date = {}
    for s in indicators:
        indicator_by_date[s["date"]] = s

    out = []
    for i, s in enumerate(dailySummaires):
        current_date = s["date"]
        if current_date in indicator_by_date and indicator_by_date[current_date].get("indicators", "") and cached:
            print("Using previous indicator")
            out.append(indicator_by_date[current_date])
            continue

        if not s["summary"]:
            out.append({
                "date": current_date,
                "indicators": {},
                "aiVersion": VERSION,
            })
            continue

        print("Computing indicator for {}".format(current_date))
        currentIndicator = summariser.computeIndicators(s["summary"])
        out.append({
                "date": current_date,
                "indicators": currentIndicator,
                "aiVersion": VERSION,
        })

    storage.writeIndicator(userId, out)



def process_data_for_demo():
    def _patch_conversation(userId):
        conversations = storage.readConversation(userId)
        for date in conversations:
            for conversation in date["conversation"]:
                if "content" not in conversation:
                    if "human" in conversation:
                        conversation["content"] = {
                            "human": conversation.pop("human")
                        }
                    
                    if "ai" in conversation:
                        conversation["content"] = {
                            "ai": conversation.pop("ai")
                        }
        storage.writeConversation(userId, conversations)

    # Prepare the topic for current day
    # Get the summary for previous days

    for userId in [0]:
        # Patch conversation
        print("1. Patching the conversation data to the new format")
        _patch_conversation(userId)

        print("2. Extract insights from the medical and carer inputs")
        insights_from_description(userId)
        
        # prepare_topic 
        print("3. Let AI preparing topics for initialising the personalised converssation with the patient")
        print("For the first running of the day, it might take a while to run...")
        print("This feature will be called once a day!")
        prepare_topic(userId, get_today())

        print("4. Summarize all conversatons of previous days")
        _summarize_all_previous_conversation(userId, cached=True)

        print("5. Generate health record")
        _compute_indicator_all_previous_conversation(userId, cached=True)

        print("Done!")

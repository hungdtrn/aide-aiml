import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

import datetime
import storage

from ai import VERSION, MODELS, build_chat_session, build_summariser, build_feat_extractor
AI_MODEL = MODELS.CHATGPT

def get_today():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def get_now():
    return datetime.datetime.now().isoformat()


def get_ai_extracted_user_details(userId):
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
        feat_extractor = build_feat_extractor(AI_MODEL)
        newDetails = {
            "id": (lastCarerInput["id"], lastMedicalInput["id"]),
            "details": feat_extractor.extractFromDescription(lastCarerInput["details"], lastMedicalInput["details"]),
        }
        if not user.get("ai_details", []):
            user["ai_details"] = [newDetails]
        else:
            user["ai_details"].append(newDetails)
        storage.updateUser(userId, user)
    
    return user["ai_details"]

def get_details_from_conversation(conversation):
    feat_extractor = build_feat_extractor(AI_MODEL)
    return feat_extractor.extractFromConversation(conversation)

from .chatgpt import ChatGPT

def build_chat_model(model_type, conversations, carerInput, medicalInput):
    if model_type == "chatgpt":
        return ChatGPT(conversations, carerInput, medicalInput)
    else:
        raise Exception(f"Invalid model type: {model_type}")

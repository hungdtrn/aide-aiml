from .chatgpt import ChatGPT

def build_chat_model(model_type, history, carerInput, medicalInput):
    if model_type == "chatgpt":
        return ChatGPT(history, carerInput, medicalInput)
    else:
        raise Exception(f"Invalid model type: {model_type}")

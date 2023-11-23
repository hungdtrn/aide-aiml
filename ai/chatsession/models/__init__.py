from .chatgpt import ChatGPT

def build_chat_model(model_type, conversations, patient_info, topics):
    if model_type == "chatgpt":
        return ChatGPT(conversations, patient_info, topics)
    else:
        raise Exception(f"Invalid model type: {model_type}")

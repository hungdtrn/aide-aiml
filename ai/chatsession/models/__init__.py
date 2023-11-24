from .chatgpt import ChatGPT

def build_chat_model(model_type, retriever, conversations, patient_info, topics, device):
    if model_type == "chatgpt":
        return ChatGPT(retriever, conversations, patient_info, topics, device)
    else:
        raise Exception(f"Invalid model type: {model_type}")

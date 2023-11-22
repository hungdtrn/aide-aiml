from .chatgpt import ChatGPT

def build_model(model_type):
    if model_type == "chatgpt":
        return ChatGPT()
    else:
        raise Exception(f"Invalid model type: {model_type}")

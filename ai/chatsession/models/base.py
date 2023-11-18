def build_chat_model(model_type, history):
    if model_type == "chatgpt":
        return ChatGPT(history)
    else:
        raise Exception(f"Invalid model type: {model_type}")

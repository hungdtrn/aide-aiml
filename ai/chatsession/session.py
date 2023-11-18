from .models import build_chat_model

class ChatSession:
    def __init__(self, history=None, model_type="chatgpt") -> None:

        self.history = history
        self.chatModel = build_chat_model(model_type, history)

    def welcome(self):
        if self.history:
            msg = "Welcome back!"
        else:
            msg = "Hello! It's great to know you!"
        
        return msg

    def chat(self, message):
        return self.chatModel.chat(message)

    def summary(self):
        return self.chatModel.summary()
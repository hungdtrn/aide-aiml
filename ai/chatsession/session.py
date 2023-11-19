from .models import build_chat_model

class ChatSession:
    def __init__(self, history=None, model_type="chatgpt") -> None:

        self.history = history
        self.chatModel = build_chat_model(model_type, history)

    def welcome(self):
        if self.history:
            msg = "Welcome back!"
        else:
            msg = "Hi! Please tell me about your day, or tell me how you are feeling "

        return msg

    def chat(self, message, streaming=False):
        return self.chatModel.chat(message, streaming)

    def summary(self):
        return self.chatModel.summary()

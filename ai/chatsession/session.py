from .models import build_chat_model

class ChatSession:
    def __init__(self, conversations=None, 
                 carerInput=None, medicalInput=None,
                 model_type="chatgpt") -> None:

        self.conversations = conversations
        self.chatModel = build_chat_model(model_type, conversations)
        self.human_prefix = self.chatModel.human_prefix
        self.ai_prefix = self.chatModel.ai_prefix

    def welcome(self):
        if self.conversations:
            msg = "Welcome back!"
        else:
            msg = "Hi! Please tell me about your day, or tell me how you are feeling "

        return msg

    def chat(self, message, streaming=False):
        return self.chatModel.chat(message, streaming)

    def summary(self):
        return self.chatModel.summary()

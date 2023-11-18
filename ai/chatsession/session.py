class ChatSession:
    def __init__(self, history=None, model_type="chatgpt") -> None:
        self.history = history

    def welcome(self):
        if self.history:
            msg = "Welcome back!"
        else:
            msg = "Hello! It's great to know you!"
        
        return msg

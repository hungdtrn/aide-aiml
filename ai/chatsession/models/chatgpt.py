import os
import openai

from langchain.chat_models import ChatOpenAI

from .base import BaseModel

class ChatGPT(BaseModel):
    def __init__(self, history) -> None:
        super().__init__(history)

        api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = api_key    
        self.model = ChatOpenAI(temperature=.7, model_name="gpt-3.5-turbo")
        self.summary_model = ChatOpenAI(temperature=.7, model_name="gpt-3.5-turbo") 

        self.human_prefix = "Human"
        self.ai_prefix = "AI"

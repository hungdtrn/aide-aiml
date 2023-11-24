import os
import openai

from langchain.chat_models import ChatOpenAI

from .base import BaseModel

class ChatGPT(BaseModel):
    human_prefix = "human"
    ai_prefix = "ai"
    def __init__(self, retriever, conversations, carerInput, medicalInput) -> None:
        super().__init__(retriever, conversations, carerInput, medicalInput)

        api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = api_key    
        self.model = ChatOpenAI(temperature=.7, model_name="gpt-3.5-turbo")

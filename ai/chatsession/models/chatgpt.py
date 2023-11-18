import os
import time
import openai
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.schema import (
    messages_from_dict, messages_to_dict
)

class ChatGPT:
    def __init__(self, history) -> None:
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = api_key    

        self.n_old_msgs = 0
        self.history = history
        self.model = ChatOpenAI(temperature=.7, model_name="gpt-3.5-turbo") 
        
        if self.history:
            self.memory = ConversationBufferMemory(chat_memory=self._loadHistoryToMemory(self.history))
        else:
            self.memory = ConversationBufferMemory()

    def _loadHistoryToMemory(self, history):
        out = []
        for sessions in history:
            for chat in sessions["conversation"]:
                for k, v in chat.items():
                    currentDict = {
                        "type": k,
                        "data": {
                            "content": v,
                            "additional_kwargs": {}
                        }
                    }
                    out.append(currentDict)
        self.n_old_msgs = len(out)
        retrieved_messages = messages_from_dict(out)
        retrieved_chat_history = ChatMessageHistory(messages=retrieved_messages)
        return retrieved_chat_history

    def chat(self, message):
        
        prompt = """The following is a friendly conversation between a human and an AI Therapist. The AI is friendly and supportive to the human. The AI's responses should prioritize the well-being of the human and avoid saying anything harmful.

Current conversation:
{history}

Human: {input}
AI: """
        prompt = PromptTemplate.from_template(prompt)
        chain = ConversationChain(
            prompt=prompt,
            llm=self.model,
            memory=self.memory
        )
        return chain(message)["response"]
    
    def summary(self):
        messages = self.memory.chat_memory.messages
        ingest_to_db = messages_to_dict(messages)
        conversations = []
        for item in ingest_to_db[self.n_old_msgs:]:
            conversations.append({
                item["type"]: item["data"]["content"]
            })
        self.history.append({
            "date": time.time(),
            "conversation": conversations,
        })
        self.history[-1]["currentSummary"] = "TODO"
        self.history[-1]["longtermSummary"] = "TODO"

        # messages up to this time are summarized
        # new messages will be concidered new conversation
        self.n_old_msgs = len(ingest_to_db)

        return self.history

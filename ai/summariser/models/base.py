import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import time
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain, LLMChain
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.schema import (
    LLMResult,
    messages_from_dict, messages_to_dict
)
# from langchain.callbacks.streaming_stdout import BaseCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler
from queue import Queue
from threading import Event, Thread
from typing import Any, Generator, Union
from prompts import get_template

class BaseModel:
    human_prefix = ""
    ai_prefix = ""
    model = None
    def __init__(self) -> None:
        load_dotenv()
    
    
    def _dailySummary(self, currentConversation):
        templates = get_template()
        dailySummary_template = templates.format_prompt(templates.DAILY_SUMMARY,
                                                                human_prefix=self.human_prefix,
                                                                ai_prefix=self.ai_prefix)
        dailySummary_prompt = PromptTemplate(input_variables=["new_lines"],
                                                     template=dailySummary_template)
        conversation_chain = LLMChain(llm=self.model, prompt=dailySummary_prompt)

        dailySummary = conversation_chain(currentConversation)["text"]
        return dailySummary
    
    def _devSummary(self, pastSummary, currentConversation):
        templates = get_template()
        
        devSummary_template = templates.format_prompt(templates.DEVELOPMENT_SUMMARY,
                                                               human_prefix=self.human_prefix,
                                                               ai_prefix=self.ai_prefix)

        
        devSummary_prompt = PromptTemplate(template=devSummary_template,
                                                    input_variables=["summary", "new_lines"])

        development_chain = LLMChain(llm=self.model, prompt=devSummary_prompt)
        devSummary = development_chain({"summary": pastSummary, 
                                        "new_lines": currentConversation})["text"]

        return devSummary

    def dailySummary(self, conversation):
        currentSummary = self._dailySummary(conversation)
        return currentSummary

    def devSummary(self, pastSummary, conversation):
        devSummary = self._devSummary(pastSummary, conversation)
        return devSummary


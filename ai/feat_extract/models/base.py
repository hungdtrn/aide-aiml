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
        self.prompt_templates = get_template()
    
    def _convert_to_list(self, text):
        info_list = text.split("\n")
        newList = []
        for item in info_list:
            item = item.replace("-", "").strip()
            if item:
                newList.append(item)
        return newList


    def extractFromDescription(self, medicalInput, carerInput):
        patient_info_template = self.prompt_templates.get_prompt_template(self.prompt_templates.PATIENT_INFO_EXTRACTION,
                                                                human_prefix=self.human_prefix,
                                                                ai_prefix=self.ai_prefix)
        patient_info_prompt = PromptTemplate(input_variables=["patient_description"],
                                             template=patient_info_template)
        patient_info_chain = LLMChain(llm=self.model, prompt=patient_info_prompt)
        patient_info = patient_info_chain({"patient_description": f"{medicalInput}\n\n{carerInput}"})["text"]
        return self._convert_to_list(patient_info)

    def extractFromConversation(self, conversation):
        conversation_info_template = self.prompt_templates.get_prompt_template(self.prompt_templates.CONVERSATION_INFO_EXTRACTION,
                                                                            human_prefix=self.human_prefix,
                                                                            ai_prefix=self.ai_prefix)
        conversation_info_prompt = PromptTemplate(input_variables=["conversation"],
                                                template=conversation_info_template)
        conversation_info_chain = LLMChain(llm=self.model, prompt=conversation_info_prompt)
        conversation_info = conversation_info_chain({"conversation": conversation})["text"]
        return self._convert_to_list(conversation_info)


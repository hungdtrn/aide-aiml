import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.chains.conversation.memory import ConversationBufferMemory

# from langchain.callbacks.streaming_stdout import BaseCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler
from queue import Queue
from threading import Event, Thread
from typing import Any, Generator, Union
from prompts import get_template

from ai_utils import run_with_timeout_retry, conversation_to_string

class BaseModel:
    human_prefix = ""
    ai_prefix = ""
    model = None
    n_topics = 5
    
    def __init__(self) -> None:
        load_dotenv()
        self.prompt_templates = get_template()
    
    def _convert_insights_to_list(self, text):
        info_list = text.split("\n")
        newList = []
        for item in info_list:
            item = item.replace("-", "").strip()
            if item:
                newList.append(item)
        return newList
    
    def _append_date_to_info_list(self, conversation_info_list):
        """ Append dates to each of the information
        """
        info = []
        for conv in conversation_info_list:
            info.append("{} - {}".format(conv["date"], conv["information"]))
        return info
    

    def insights_from_description(self, medicalInput, carerInput):
        patient_info_template = self.prompt_templates.get_prompt_template(self.prompt_templates.PATIENT_INFO_EXTRACTION,
                                                                human_prefix=self.human_prefix,
                                                                ai_prefix=self.ai_prefix)
        patient_info_prompt = PromptTemplate(input_variables=["patient_description"],
                                             template=patient_info_template)
        patient_info_chain = LLMChain(llm=self.model, prompt=patient_info_prompt)
        patient_info = run_with_timeout_retry(patient_info_chain, {"patient_description": f"{medicalInput}\n\n{carerInput}"})["text"]
        return self._convert_insights_to_list(patient_info)

    def insights_from_conversation(self, conversation):
        conversation = self.conversation_to_string(conversation)
        conversation_info_template = self.prompt_templates.get_prompt_template(self.prompt_templates.CONVERSATION_INFO_EXTRACTION,
                                                                            human_prefix=self.human_prefix,
                                                                            ai_prefix=self.ai_prefix)
        conversation_info_prompt = PromptTemplate(input_variables=["conversation"],
                                                template=conversation_info_template)
        conversation_info_chain = LLMChain(llm=self.model, prompt=conversation_info_prompt)
        conversation_info = run_with_timeout_retry(conversation_info_chain, {"conversation": conversation})["text"]
        return self._convert_insights_to_list(conversation_info)


    def topic_suggestions(self, patient_info, conversation_info):
        conv_info = self._append_date_to_info_list(conversation_info)
        
        if not conv_info:
            topic_suggestion_template = self.prompt_templates.get_prompt_template(self.prompt_templates.TOPIC_SUGGESTION_WITHOUT_CONVERSATION,
                                                                                        human_prefix=self.human_prefix,
                                                                                        ai_prefix=self.ai_prefix)
            topic_suggestion_prompt = PromptTemplate(input_variables=["patient_info", "n_topics"],
                                                    template=topic_suggestion_template)
            topic_suggestion_chain = LLMChain(llm=self.model, prompt=topic_suggestion_prompt)
            input_dict = {"patient_info": patient_info,
                                                       "n_topics": self.n_topics}
        else:
            topic_suggestion_template = self.prompt_templates.get_prompt_template(self.prompt_templates.TOPIC_SUGGESTION_WITH_CONVERSATION,
                                                                                        human_prefix=self.human_prefix,
                                                                                        ai_prefix=self.ai_prefix)
            topic_suggestion_prompt = PromptTemplate(input_variables=["patient_info", "previous_insight", "n_topics"],
                                                    template=topic_suggestion_template)
            topic_suggestion_chain = LLMChain(llm=self.model, prompt=topic_suggestion_prompt)
            input_dict = {"patient_info": patient_info,
                                                       "previous_insight": conv_info,
                                                       "n_topics": self.n_topics}

        topic_suggestion = run_with_timeout_retry(topic_suggestion_chain, input_dict)["text"]
        print(topic_suggestion)
        return topic_suggestion

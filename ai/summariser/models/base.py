import os
import json
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
from ai_utils import run_with_timeout_retry, conversation_to_string, chunk_conversation, progressive_summarise, MAX_CONV_LENGTH

class BaseModel:
    human_prefix = ""
    ai_prefix = ""
    model = None
    def __init__(self) -> None:
        load_dotenv()
        self.prompt_templates = get_template()
    
    def dailySummary(self, conversation):
        conversation = conversation_to_string(conversation, to_string=False)
        conversation, follow_up_conv = chunk_conversation(conversation)

        dailySummary_template = self.prompt_templates.get_prompt_template(self.prompt_templates.DAILY_SUMMARY,
                                                        human_prefix=self.human_prefix,
                                                        ai_prefix=self.ai_prefix)
        dailySummary_prompt = PromptTemplate(input_variables=["conversation"],
                                                     template=dailySummary_template)

        conversation_chain = LLMChain(llm=self.model, prompt=dailySummary_prompt)

        dailySummary = run_with_timeout_retry(conversation_chain, {"conversation": "\n".join(conversation)})["text"]
        
        if follow_up_conv:
            devSummary_template = self.prompt_templates.get_prompt_template(self.prompt_templates.DEVELOPMENT_SUMMARY,
                                                                        human_prefix=self.human_prefix,
                                                                        ai_prefix=self.ai_prefix)
            devSummary_prompt = PromptTemplate(template=devSummary_template,
                                                input_variables=["summary", "conversation"])

            development_chain = LLMChain(llm=self.model, prompt=devSummary_prompt)

            dailySummary = progressive_summarise(development_chain, dailySummary, follow_up_conv)


        return dailySummary
    

    def devSummary(self, pastSummary, conversation):
        conversation = conversation_to_string(conversation, to_string=False)
        conversation, follow_up_conv = chunk_conversation(conversation)
        follow_up_conv = [conversation] + follow_up_conv

        devSummary_template = self.prompt_templates.get_prompt_template(self.prompt_templates.DEVELOPMENT_SUMMARY,
                                                               human_prefix=self.human_prefix,
                                                               ai_prefix=self.ai_prefix)

        
        devSummary_prompt = PromptTemplate(template=devSummary_template,
                                                    input_variables=["summary", "conversation"])

        development_chain = LLMChain(llm=self.model, prompt=devSummary_prompt)
        devSummary = progressive_summarise(development_chain, pastSummary, follow_up_conv)

        return devSummary
    
    def computeIndicators(self, dailySummary):
        indicator_template = self.prompt_templates.get_prompt_template(self.prompt_templates.INDICATOR,
                                                               human_prefix=self.human_prefix,
                                                               ai_prefix=self.ai_prefix)
        indicator_prompt = PromptTemplate(template=indicator_template,
                                          input_variables=["summary"])

        indicator_chain = LLMChain(llm=self.model, prompt=indicator_prompt)

        indicator = {}
        for i in range(3):
            try:
                indicator = run_with_timeout_retry(indicator_chain, {"summary": dailySummary})["text"]
                indicator = json.loads(indicator)
                break
            except Exception as e:
                print(e)
                print("Retrying")

        return indicator




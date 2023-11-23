import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import time
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain, LLMChain
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.chains.conversation.memory import ConversationBufferMemory, ConversationBufferWindowMemory
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
from ai_utils import get_today, run_with_timeout_retry


class StreamingGeneratorCallbackHandler(BaseCallbackHandler):
    """Streaming callback handler. Copied from LlamaIndex"""

    def __init__(self) -> None:
        self._token_queue: Queue = Queue()
        self._done = Event()

    def __deepcopy__(self, memo: Any) -> "StreamingGeneratorCallbackHandler":
        # NOTE: hack to bypass deepcopy in langchain
        return self

    def on_llm_new_token(self, token: str, **kwargs: Any) -> Any:
        """Run on new LLM token. Only available when streaming is enabled."""
        self._token_queue.put_nowait(token)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        self._done.set()

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        self._done.set()

    def get_response_gen(self) -> Generator:
        while True:
            if not self._token_queue.empty():
                token = self._token_queue.get_nowait()
                yield token
            elif self._done.is_set():
                break


class BaseModel:
    human_prefix = ""
    ai_prefix = ""
    model = None
    NUM_SHORT_TERM_CONVERSATION = 5

    def __init__(self, conversations, patient_info, topics) -> None:
        load_dotenv()
        self.prompt_templates = get_template()

        self.patient_info = patient_info
        self.topics = topics
        
        self.conversations = conversations

        if conversations:
            self.memory = ConversationBufferWindowMemory(chat_memory=self._loadConversationsToMemory(conversations),
                                                         k=self.NUM_SHORT_TERM_CONVERSATION)
        else:
            self.memory = ConversationBufferWindowMemory(k=self.NUM_SHORT_TERM_CONVERSATION)
        

    def _loadConversationsToMemory(self, conversations):
        out = []
        for sessions in conversations:
            for chat in sessions["conversation"]:
                for k, v in chat["content"].items():
                    if k != self.ai_prefix and k != self.human_prefix:
                        continue

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
    
    def _chat(self, message, **kwargs):
        # Get the prompt templates based on (1) the device and (2) the client
        template_head = self.prompt_templates.get_prompt_template(self.prompt_templates.CHAT_HEAD,
                                                  human_prefix=self.human_prefix, ai_prefix=self.ai_prefix)
        template_body = self.prompt_templates.get_prompt_template(self.prompt_templates.CHAT_BODY,
                                                                  human_prefix=self.human_prefix, ai_prefix=self.ai_prefix)
        template_head = template_head.format(
            patient_info=self.patient_info,
            retrive_context="",
            suggested_topics=self.topics,
            today=get_today(),
        )

        template = template_head + template_body

        prompt = PromptTemplate.from_template(template)
        print(prompt)
        chain = ConversationChain(
            prompt=prompt,
            llm=self.model,
            memory=self.memory
        )
        return run_with_timeout_retry(chain, message)


    def _welcome(self):
        if self.conversations and self.conversations[-1]["date"] == get_today() and self.conversations[-1]["conversation"]:
            # Welcome back message
            template = self.prompt_templates.get_prompt_template(self.prompt_templates.WELCOME_MESSAGE_CONTINUE_CONVERSATION,
                                                                 human_prefix=self.human_prefix, ai_prefix=self.ai_prefix)
            prompt = PromptTemplate.from_template(template)
            prompt_input = {
                "patient_info": self.patient_info,
                "topics": self.topics,
                "conversation":  self.memory.buffer_as_str,
            }
        else:
            print("starting a new")
            # Welcome new conversation message. 
            template = self.prompt_templates.get_prompt_template(self.prompt_templates.WELCOME_MESSAGE_NEW_CONVERSATION,
                                                                 human_prefix=self.human_prefix, ai_prefix=self.ai_prefix)
            prompt = PromptTemplate.from_template(template)
            prompt_input = {
                "patient_info": self.patient_info,
                "topics": self.topics,
            }

        chain = LLMChain(llm=self.model, prompt=prompt)
        out = run_with_timeout_retry(chain, prompt_input)
        return out


    def welcome(self, streaming=True):
        print("In welcome", streaming)
        if not streaming:
            self.model.streaming = False
            self.model.callbacks = []
            return self._welcome()["text"]
        else:
            self.model.streaming = True
            # COPY from LlamaIndex
            handler = StreamingGeneratorCallbackHandler()
            self.model.callbacks = [handler]
            thread = Thread(target=self._welcome, args=[], kwargs={})
            thread.start()
            response_gen = handler.get_response_gen()
            return response_gen


    def chat(self, message, streaming):
        if not streaming:
            self.model.streaming = False
            self.model.callbacks = []
            return self._chat(message)["response"]
        else:
            self.model.streaming = True
            # COPY from LlamaIndex
            handler = StreamingGeneratorCallbackHandler()
            self.model.callbacks = [handler]
            thread = Thread(target=self._chat, args=[message], kwargs={})
            
            thread.start()
            response_gen = handler.get_response_gen()
            return response_gen


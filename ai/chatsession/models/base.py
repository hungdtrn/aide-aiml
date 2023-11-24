import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import random
import time
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain, LLMChain
from langchain.chains.conversation.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.schema import (
    LLMResult,
)
# from langchain.callbacks.streaming_stdout import BaseCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler
from queue import Queue
from threading import Event, Thread
from typing import Any, Generator, Union
from prompts import get_template
from ai_utils import get_today, get_now, run_with_timeout_retry, loadAllConversationsToMemory


class StreamingGeneratorCallbackHandler(BaseCallbackHandler):
    """Streaming callback handler. Copied from LlamaIndex"""

    def __init__(self) -> None:
        self._token_queue: Queue = Queue()
        self.llm_response = None
        self._done = Event()

    def __deepcopy__(self, memo: Any) -> "StreamingGeneratorCallbackHandler":
        # NOTE: hack to bypass deepcopy in langchain
        return self

    def on_llm_new_token(self, token: str, **kwargs: Any) -> Any:
        """Run on new LLM token. Only available when streaming is enabled."""
        self._token_queue.put_nowait(token)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        self.llm_response = response
        self._done.set()

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        self._done.set()

    def get_response_gen(self) -> Generator:
        while True:
            if not self._token_queue.empty():
                token = self._token_queue.get_nowait()
                yield token, self.llm_response
            elif self._done.is_set():
                yield "", self.llm_response
                break


class BaseModel:
    human_prefix = ""
    ai_prefix = ""
    model = None
    NUM_SHORT_TERM_CONVERSATION = 5

    def __init__(self, retriever, conversations, patient_info, topics, device="streamlit") -> None:
        load_dotenv()
        self.prompt_templates = get_template(device=device)
        self.retriever = retriever

        self.patient_info = patient_info
        self.topics = topics
        
        self.conversations = conversations
        self.reload_memory(conversations)

        
    def reload_memory(self, conversations):
        if conversations:
            self.memory = ConversationBufferWindowMemory(chat_memory=loadAllConversationsToMemory(conversations, self.ai_prefix, self.human_prefix),
                                                         k=self.NUM_SHORT_TERM_CONVERSATION)
        else:
            self.memory = ConversationBufferWindowMemory(k=self.NUM_SHORT_TERM_CONVERSATION)

    
    def _chat(self, message, **kwargs):
        random.shuffle(self.topics)
        # Get the prompt templates based on (1) the device and (2) the client
        template_head = self.prompt_templates.get_prompt_template(self.prompt_templates.CHAT_HEAD,
                                                  human_prefix=self.human_prefix, ai_prefix=self.ai_prefix)
        template_body = self.prompt_templates.get_prompt_template(self.prompt_templates.CHAT_BODY,
                                                                  human_prefix=self.human_prefix, ai_prefix=self.ai_prefix)
        
        if self.conversations:
            context = self.retriever.query(message)
            context = "\n".join(context)
        else:
            context = ""
            
        template_head = template_head.format(
            patient_info=self.patient_info,
            retrive_context=context,
            suggested_topics="\n".join(self.topics),
            now=get_now(),
        )

        template = template_head + template_body

        prompt = PromptTemplate.from_template(template)
        chain = ConversationChain(
            prompt=prompt,
            llm=self.model,
            memory=self.memory
        )
        print(chain.prompt, self.memory.buffer_as_str)
        return run_with_timeout_retry(chain, message, timeout=20)


    def _welcome(self):
        random.shuffle(self.topics)
        if self.conversations and self.conversations[-1]["date"] == get_today() and self.conversations[-1]["conversation"]:
            # Welcome back message
            template = self.prompt_templates.get_prompt_template(self.prompt_templates.WELCOME_MESSAGE_CONTINUE_CONVERSATION,
                                                                 human_prefix=self.human_prefix, ai_prefix=self.ai_prefix)
            prompt = PromptTemplate.from_template(template)
            prompt_input = {
                "now": get_now(),
                "patient_info": self.patient_info,
                "topics": "\n".join(self.topics),
                "conversation":  self.memory.buffer_as_str,
            }
        else:
            # Welcome new conversation message. 
            template = self.prompt_templates.get_prompt_template(self.prompt_templates.WELCOME_MESSAGE_NEW_CONVERSATION,
                                                                 human_prefix=self.human_prefix, ai_prefix=self.ai_prefix)
            prompt = PromptTemplate.from_template(template)
            prompt_input = {
                "now": get_now(),
                "patient_info": self.patient_info,
                "topics":  "\n".join(self.topics),
            }

        print(prompt_input, prompt)
        chain = LLMChain(llm=self.model, prompt=prompt)
        out = run_with_timeout_retry(chain, prompt_input, timeout=30)
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

    
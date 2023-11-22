import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

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
    def __init__(self, history, carerInput, medicalInput) -> None:
        load_dotenv()
        
        if history:
            self.memory = ConversationBufferMemory(chat_memory=self._loadHistoryToMemory(history))
        else:
            self.memory = ConversationBufferMemory()

    def _loadHistoryToMemory(self, history):
        out = []
        for sessions in history:
            for chat in sessions["conversation"]:
                for k, v in chat.items():
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
        templates = get_template()
        prompt_template = templates.format_prompt(templates.CHAT_TEMPLATE,
                                                  human_prefix=self.human_prefix, ai_prefix=self.ai_prefix)

        prompt = PromptTemplate.from_template(prompt_template)
        chain = ConversationChain(
            prompt=prompt,
            llm=self.model,
            memory=self.memory
        )
        return chain(message)
    
    def _dailySummary(self, currentConversation):
        templates = get_template()
        dailySummary_template = templates.format_prompt(templates.DAILY_SUMMARY_TEMPLATE,
                                                                human_prefix=self.human_prefix,
                                                                ai_prefix=self.ai_prefix)
        dailySummary_prompt = PromptTemplate(input_variables=["new_lines"],
                                                     template=dailySummary_template)
        conversation_chain = LLMChain(llm=self.model, prompt=dailySummary_prompt)

        dailySummary = conversation_chain(currentConversation)["text"]
        return dailySummary
    
    def _devSummary(self, pastSummary, currentConversation):
        templates = get_template()
        
        devSummary_template = templates.format_prompt(templates.DEVELOPMENT_SUMMARY_TEMPLATE,
                                                               human_prefix=self.human_prefix,
                                                               ai_prefix=self.ai_prefix)

        
        devSummary_prompt = PromptTemplate(template=devSummary_template,
                                                    input_variables=["summary", "new_lines"])

        development_chain = LLMChain(llm=self.model, prompt=devSummary_prompt)
        devSummary = development_chain({"summary": pastSummary, 
                                        "new_lines": currentConversation})["text"]

        return devSummary

    def dailySummary(self, conversation):
        self.model.streaming = False
        self.model.callbacks = []
        currentSummary = self._dailySummary(conversation)
        return currentSummary

    def devSummary(self, pastSummary, conversation):
        self.model.streaming = False
        self.model.callbacks = []
        devSummary = self._devSummary(pastSummary, conversation)
        return devSummary

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


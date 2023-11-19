import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

import time
import openai
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
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


class ChatGPT:
    def __init__(self, history) -> None:
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = api_key    

        self.n_old_msgs = 0
        self.history = history
        self.model = ChatOpenAI(temperature=.7, model_name="gpt-3.5-turbo")
        self.summary_model = ChatOpenAI(temperature=.7, model_name="gpt-3.5-turbo") 
        
        if self.history:
            self.memory = ConversationBufferMemory(chat_memory=self._loadHistoryToMemory(self.history))
        else:
            self.memory = ConversationBufferMemory()

        self.human_prefix = "Human"
        self.ai_prefix = "AI"

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

    def _chat(self, message, **kwargs):
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

    def _update_history(self):
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
        self.n_old_msgs = len(ingest_to_db)

    def _conversation2string(self, converstaion):
        out = ""
        for item in converstaion:
            for k, v in item.items():
                out += "{}: {}".format(k, v) + "\n"
        return out    

    def _conversation_summary(self, currentConversation):
        templates = get_template()
        conversation_summary_template = templates.format_prompt(templates.CONVERSATION_SUMMARY_TEMPLATE,
                                                                human_prefix=self.human_prefix,
                                                                ai_prefix=self.ai_prefix)
        conversation_summary_prompt = PromptTemplate(input_variables=["new_lines"],
                                                     template=conversation_summary_template)
        conversation_chain = LLMChain(llm=self.model, prompt=conversation_summary_prompt)

        conversation_summary = conversation_chain(currentConversation)["text"]
        return conversation_summary
    
    def _development_summary(self, currentConversation):
        templates = get_template()
        
        development_summary_template = templates.format_prompt(templates.DEVELOPMENT_SUMMARY_TEMPLATE,
                                                               human_prefix=self.human_prefix,
                                                               ai_prefix=self.ai_prefix)

        
        development_summary_prompt = PromptTemplate(template=development_summary_template,
                                                    input_variables=["summary", "new_lines"])

        development_chain = LLMChain(llm=self.model, prompt=development_summary_prompt)
        pastSummary = self.history[-2].get("longtermSummary", "")
        development_summary = development_chain({"summary": pastSummary, 
                                                    "new_lines": currentConversation})["text"]

        return development_summary

    def _summary(self):
        """ Do two things:
        1. Summary the conversation in the current session - conversationSummary
        2. Summary the development of the patient's mental state so far - developmentSummary
        """
        currentConversation = self.history[-1]["conversation"]
        currentSummary = self._conversation_summary(currentConversation)
        if len(self.history) <= 1:
            developmentSummary = currentSummary
        else:
            developmentSummary = self._development_summary(currentConversation)

        return currentSummary, developmentSummary


    def summary(self):
        # Update the history conversation
        self._update_history()

        # Summarise the conversation
        self.model.streaming = False
        self.model.callbacks = []
        
        conversation_summary, development_summary = self._summary()
        self.history[-1]["conversationSummary"] = conversation_summary
        self.history[-1]["developmentSummary"] = development_summary
        
        # messages up to this time are summarized
        # new messages will be concidered new conversation

        return self.history

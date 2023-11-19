import os
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

    def _chat(self, message, **kwargs):
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

    def _summary(self):
        currentConversation = self.history[-1]["conversation"]
        short_summary_prompt_template = """This is a conversation between a patient and an AI Therapist. Summarize the patient's emotional state. This summary will be used to assess the patient's mental health.

{new_lines}
"""    
        short_summary_prompt = PromptTemplate(input_variables=["new_lines"],
                                              template=short_summary_prompt_template)
        short_summary_chain = LLMChain(llm=self.model, prompt=short_summary_prompt)
        out = short_summary_chain(currentConversation)["text"]
        return out


    def summary(self):
        # Update the history conversation
        self._update_history()

        # Summarise the conversation
        self.model.streaming = False
        self.model.callbacks = []
        
        short_summary = self._summary()
        self.history[-1]["currentSummary"] = short_summary
        self.history[-1]["longtermSummary"] = "TODO"
        
        # messages up to this time are summarized
        # new messages will be concidered new conversation

        return self.history

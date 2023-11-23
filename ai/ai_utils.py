import time
import datetime

from langchain.schema import (
    LLMResult,
    messages_from_dict, messages_to_dict
)

from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from openai.error import Timeout as OpenAITimeoutError

TIMEOUT = 120
TIMEOUT_RETRY = 3

def get_today():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def get_now():
    return datetime.datetime.now().isoformat()

def run_with_timeout_retry(chain, chain_input):
    chain.llm.request_timeout = TIMEOUT
    for i in range(TIMEOUT_RETRY):
        try:
            return chain(chain_input)
        except OpenAITimeoutError as e:
            print("Retrying...")
            time.sleep(1)
    raise Exception("Timeout")

def loadConversationOneDay(conversation, ai_prefix, human_prefix):
    out = []
    for chat in conversation["conversation"]:
        for k, v in chat["content"].items():
            if k.lower() != ai_prefix.lower() and k.lower() != human_prefix.lower():
                continue

            currentDict = {
                "type": k,
                "data": {
                    "content": v,
                    "additional_kwargs": {}
                }
            }
            out.append(currentDict)
    
    return out


def conversation_to_string(conversation, to_string=True):
    """ Convert the converstation dicct list to covnersation string list
    """
    if to_string:
        out = ""
    else:
        out = []

    for line in conversation["conversation"]:
        for k, v in line["content"].items():

            if to_string:
                out += "{}: {}\n".format(k, v)
            else:
                out.append("{}: {}".format(k, v))

    return out



def loadAllConversationsToMemory(conversations, ai_prefix, human_prefix):
    out = []
    for sessions in conversations:
        out.extend(loadConversationOneDay(sessions, ai_prefix, human_prefix))

    retrieved_messages = messages_from_dict(out)
    retrieved_chat_history = ChatMessageHistory(messages=retrieved_messages)
    return retrieved_chat_history

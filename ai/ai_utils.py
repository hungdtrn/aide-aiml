import time
import datetime
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
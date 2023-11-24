from .chatsession import build_chat_session
from .summariser import build_summariser
from .conversation_prompter import build_conversation_prompter
from ai.ai_utils import get_now, get_today, PREV_CONV_IN_TOPIC, RANDOM_CONV_IN_TOPIC

VERSION = "v1"
class MODELS:
    CHATGPT = "chatgpt"
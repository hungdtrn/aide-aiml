from .base import BasePropmtTemplates

def get_by_target(target):
    if target == "mental":
        return MentalHealthPrompt()
    elif target == "elder":
        return ElderlyPrompt()
    

class MentalHealthPrompt(BasePropmtTemplates):
    CHAT = """The following is a friendly conversation between a human and an AI Assistant. The AI is friendly and supportive to the human. The AI's responses should prioritize the well-being of the human and avoid saying anything harmful.

Current conversation:
{history}

<human_prefix>: {input}
<ai_prefix>:"""   

    DAILY_SUMMARY =  """This is a conversation between a patient and an AI Assistant. Summarize the patient's emotional state. This summary will be used to assess the patient's mental health.

{new_lines}
"""    

    DEVELOPMENT_SUMMARY = """This is a conversation between a patient and an AI Assistant. 
Progressively summarize the patient's emotional state, building upon the previous summary to generate a new assessment of their mental health.

EXAMPLE
Current summary:
The patient is feeling bad today because they have just broken up with their girlfriend. They express sadness and hurt over the end of the relationship. They are looking for someone to talk to and seek support from.

New lines of conversation:
<human_prefix>: Could not get over her!
<ai_prefix>: Breakups can be really tough, and it's completely understandable that it may take some time to get over someone you cared about. Remember that healing takes time and it's okay to feel sad or even miss your ex. It might be helpful to focus on self-care and doing things that make you feel good. Is there anything in particular that you're finding difficult about getting over her?

New summary:
The patient is experiencing sadness and hurt from a recent breakup, struggling to get over their ex-partner. They express difficulty and sadness, indicating a need for support and understanding during this challenging time.

END OF EXAMPLE

Current summary:
{summary}

New lines of conversation:
{new_lines}

New summary:
"""

    def __init__(self) -> None:
        super().__init__()

class ElderlyPrompt(BasePropmtTemplates):
    META_INSTRUCTION = """You are an Elderly Care Assistant named AIDE. Your main duty is to cultivate engaging conversations and encourage the patient to share aspects of their life, including hobbies, relationships, preferences, concerns, issues, and health problems"""
    
    PATIENT_INFO_EXTRACTION = """<meta_instruction>. Considering the patient's description, extract relevant information for future conversations and tracking. Present the information in a succinct paragraph, highlighting key details.

Patient's description:
{patient_description}
"""

    CONVERSATION_INFO_EXTRACTION = """<meta_instruction>. Utilize information from the current conversation log to extract relevant details for future conversations. Present the information in a succinct paragraph, highlighting key details.

Current conversation:
{conversation}
"""

    TOPIC_SUGGESTION_WITHOUT_CONVERSATION = """<meta_instruction>. Utilize patient information to generate {n_topics} conversation topics for future interactions, ensuring to exclude disliked topics and avoid repetition. For each topic, collect related context from the provided information that can be used to initiate the conversation. Present the list in bullet points in the provided response format. Present the list in bullet points in the provided response format.

Patient Information:
{patient_info}

Response format:
- Topic: Topic name. Context: Relevant information that can be used to initiate the conversation.
- Topic: Topic name. Context: relevant information that can be used to initiate the conversation.
...
"""

    TOPIC_SUGGESTION_WITH_CONVERSATION = """<meta_instruction>. Utilize patient information and insights from previous conversations to generate {n_topics} conversation topics for future interactions, ensuring to exclude disliked topics and avoid repetition. For each topic, collect related context from the provided information that can be used to initiate the conversation. Present the list in bullet points in the provided response format. Present the list in bullet points in the provided response format.

Patient Information:
{patient_info}

Insights from the previous conversation:
{previous_insight}

Response format:
- Topic: Topic name. Context: Relevant information that can be used to initiate the conversation.
- Topic: Topic name. Context: relevant information that can be used to initiate the conversation.
...
"""

    WELCOME_MESSAGE_NEW_CONVERSATION = """<meta_instruction>. Begin the conversation by introducing yourself, conveying your eagerness to listen and assist, and initiate with a genuine two-sentence conversation starter on a randomly chosen topic from the suggestions provided, considering the context provided with the topic and the patient information. This is your first interaction with the patient; aim for authenticity and avoid repetition. Keep the conversation real, humorous, and in at most three sentences.

Patient information:
{patient_info}

Suggested Topics:
{topics}

<ai_prefix>:
"""

    WELCOME_MESSAGE_CONTINUE_CONVERSATION = """<meta_instruction>. Since you've already had a conversation today, welcome the patient back, reintroduce yourself, and initiate with a genuine two-sentence conversation starter on a randomly chosen topic from the suggestions provided, considering the context provided with the topic and the patient information. Take into account the context provided with the topic and the patient information. Ensure to reintroduce yourself before initiating the conversation. Keep the conversation real, humorous, and in at most three sentences.

Patient information:
{patient_info}

Suggested Topics:
{topics}

Previous conversations:
{conversation}

<ai_prefix>:
"""

    # Currently the ConversationChain does not allow for custom variable. Implement some workaroud
    CHAT_HEAD = """Today is {today}. <meta_instruction>. Maintain the conversation with empathy, helpfulness, and a touch of humor, taking into consideration the patient's information and the provided context. This is a conversation, keep the dialogue short. 
    
Patient information:
{patient_info}

Suggested Topics:
{suggested_topics}

Additional context:
{retrive_context}"""

    CHAT_BODY = """
Current conversation:
{history}

<human_prefix>: {input}
<ai_prefix>:"""   

    DAILY_SUMMARY =  """<meta_instruction>. This is a conversation between you and the patient. Summarize the patient's emotional, mental, and physical state throughout the day. Use this summary to monitor and track the patient's overall well-being.

{new_lines}
"""    

    DEVELOPMENT_SUMMARY = """<meta_instruction>. This is a conversation between you and the patient for today. Progressively summarize the developemt of the patient's emotional, mental, and physical state of the patient throughout the day, expanding on the previous summary to create a new assessment of their overall well-being.
    
EXAMPLE
Current summary:
The patient is feeling bad today because they have just broken up with their girlfriend. They express sadness and hurt over the end of the relationship. They are looking for someone to talk to and seek support from.

New lines of conversation:
<human_prefix>: Could not get over her!
<ai_prefix>: Breakups can be really tough, and it's completely understandable that it may take some time to get over someone you cared about. Remember that healing takes time and it's okay to feel sad or even miss your ex. It might be helpful to focus on self-care and doing things that make you feel good. Is there anything in particular that you're finding difficult about getting over her?

New summary:
The patient is experiencing sadness and hurt from a recent breakup, struggling to get over their ex-partner. They express difficulty and sadness, indicating a need for support and understanding during this challenging time.

END OF EXAMPLE

Current summary:
{summary}

New lines of conversation:
{new_lines}

New summary:
"""

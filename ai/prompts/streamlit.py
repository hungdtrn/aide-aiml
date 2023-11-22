from .base import BasePropmtTemplates

def get_by_target(target):
    if target == "mental":
        return MentalHealthPrompt()
    elif target == "elder":
        return ElderlyPrompt()
    

class MentalHealthPrompt(BasePropmtTemplates):
    CHAT = """The following is a friendly conversation between a human and an AI Therapist. The AI is friendly and supportive to the human. The AI's responses should prioritize the well-being of the human and avoid saying anything harmful.

Current conversation:
{history}

<human_prefix>: {input}
<ai_prefix>:"""   

    DAILY_SUMMARY =  """This is a conversation between a patient and an AI Therapist. Summarize the patient's emotional state. This summary will be used to assess the patient's mental health.

{new_lines}
"""    

    DEVELOPMENT_SUMMARY = """This is a conversation between a patient and an AI Therapist. 
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
    
    PATIENT_INFO_EXTRACTION = """<meta_instruction>. Considering the patient's description, extract relevant information for future conversations and tracking. Keep the information succinct, and return a list of bullet points in the provided response format.

Patient's description:
{patient_description}

Response format:
- Detail 1
- Detail 2
...

Examples:
- name: Test
- hobbies: running, coding
"""

    CONVERSATION_INFO_EXTRACTION = """<meta_instruction>. Utilize information from the current conversation log to extract relevant details for future conversations. Return a list of bullet points in the provided response format.

Current conversation:
{conversation}

Response format:
- Detail 1
- Detail 2
...

Examples:
- The patient mentioned that he will visit his friend by tomorrow.
- The patient mentioned that about a dancing club.
"""

    CHAT = """The following is a friendly conversation between a human and an AI Therapist. The AI is friendly and supportive to the human. The AI's responses should prioritize the well-being of the human and avoid saying anything harmful.

Current conversation:
{history}

<human_prefix>: {input}
<ai_prefix>:"""   

    DAILY_SUMMARY =  """This is a conversation between a patient and an AI Therapist. Summarize the patient's emotional state. This summary will be used to assess the patient's mental health.

{new_lines}
"""    

    DEVELOPMENT_SUMMARY = """This is a conversation between a patient and an AI Therapist. 
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

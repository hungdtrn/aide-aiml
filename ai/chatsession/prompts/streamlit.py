from .base import BasePropmtTemplates

def get_template_by_target(target):
    if target == "mental":
        return MentalHealthPrompt()
    

class MentalHealthPrompt(BasePropmtTemplates):
    CHAT_TEMPLATE = """The following is a friendly conversation between a human and an AI Assistant. The AI is friendly and supportive to the human. The AI's responses should prioritize the well-being of the human and avoid saying anything harmful.

Current conversation:
{history}

<human_prefix>: {input}
<ai_prefix>:"""   

    DAILY_SUMMARY_TEMPLATE =  """This is a conversation between a patient and an AI Assistant. Summarize the patient's emotional state. This summary will be used to assess the patient's mental health.

{new_lines}
"""    

    DEVELOPMENT_SUMMARY_TEMPLATE = """This is a conversation between a patient and an AI Assistant. 
Progressively summarize the patient's emotional state, building upon the previous summary to generate a new assessment of their mental health.

EXAMPLE
Current summary:
The patient is feeling bad today because they have just broken up with their best friend. They express sadness and hurt over the end of the relationship. They are looking for someone to talk to and seek support from.

New lines of conversation:
<human_prefix>: Could not get over them !
<ai_prefix>: Breakups can be really tough, and it's completely understandable that it may take some time to get over someone you cared about. Remember that healing takes time and it's okay to feel sad or even miss your ex. It might be helpful to focus on self-care and doing things that make you feel good. Is there anything in particular that you're finding difficult about getting over them ?

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


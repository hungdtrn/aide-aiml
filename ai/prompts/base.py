class BasePropmtTemplates:
    META_INSTRUCTION = ""
    PATIENT_INFO_EXTRACTION = ""
    CONVERSATION_INFO_EXTRACTION = ""
    TOPIC_SUGGESTION_WITH_CONVERSATION = ""
    TOPIC_SUGGESTION_WITHOUT_CONVERSATION  = ""
    START_FIRST_CONVERSATION = ""
    START_CONVERSATION = ""
    INDICATOR = ""
    CHAT_FIRST_CONVERSATION = ""
    CHAT = ""
    CONVERSATION_SUMMARY = ""
    DEVELOPMENT_SUMMARY = ""
    def get_prompt_template(self, prompt, human_prefix, ai_prefix):
        return prompt.replace("<human_prefix>", human_prefix).replace("<ai_prefix>", ai_prefix).replace("<meta_instruction>", self.META_INSTRUCTION)
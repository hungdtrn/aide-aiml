class BasePropmtTemplates:
    CHAT_TEMPLATE = ""
    CONVERSATION_SUMMARY_TEMPLATE = ""
    DEVELOPMENT_SUMMARY_TEMPLATE = ""
    def format_prompt(self, prompt, human_prefix, ai_prefix):
        return prompt.replace("<human_prefix>", human_prefix).replace("<ai_prefix>", ai_prefix)
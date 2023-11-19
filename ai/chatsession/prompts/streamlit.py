from .base import BasePropmtTemplates

def get_template_by_target(target):
    if target == "mental":
        return MentalHealthPrompt()
    

class MentalHealthPrompt(BasePropmtTemplates):
    def __init__(self) -> None:
        super().__init__()

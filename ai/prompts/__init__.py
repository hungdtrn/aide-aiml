from .streamlit import get_by_target as st_get_template_by_target
from .voice import get_by_target as sound_get_template_by_target

def get_template(target="elder", device="streamlit"):
    if device == "streamlit":
        return st_get_template_by_target(target)
    elif device == "voice":
        return sound_get_template_by_target(target)
    else:
        raise Exception("not implemented")
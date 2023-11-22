from .streamlit import get_by_target as st_get_template_by_target
from .sound import get_by_target as sound_get_template_by_target

def get_template(target="mental", device="streamlit"):
    if device == "streamlit":
        return st_get_template_by_target(target)
    elif device == "sound":
        raise Exception("Not implemented yet")
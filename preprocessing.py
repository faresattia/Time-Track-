import re

def clean_text(text: str):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text
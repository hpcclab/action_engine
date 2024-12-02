def escape_json(text: str) -> str:
    return text.replace('{', '{{').replace('}', '}}')


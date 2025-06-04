import json

_translations = {}

def load_language(lang_code):
    global _translations
    with open(f"lang/{lang_code}.json", encoding="utf-8") as f:
        _translations = json.load(f)

def tr(key):
    return _translations.get(key, key)

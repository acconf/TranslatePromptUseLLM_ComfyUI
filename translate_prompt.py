import os
import json
import re
import requests
from .prompt_template import (TRANSLATE_PROMPT)

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "translate_config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "api_key": "",
        "model": "gemini-2.0-flash",
        "api_base": "https://generativelanguage.googleapis.com/v1beta/openai"
    }

class TranslatePrompt:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "positive_prompt": ("STRING", {"multiline": True}),
                "negative_prompt": ("STRING", {"multiline": True}),
                "source_lang":(["zh","ja"],
                                {"default": "zh", "label": "Source Language"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("translated_positive", "translated_negative",)
    FUNCTION = "translate"
    CATEGORY = "utils"

    def llm_translate(self, text1, text2, config, source_lang="zh"):
        
        if not text2.strip():
            text2 = "Blurry, Noisy, Distorted"

        if not text1.strip():
            return (text1, text2)

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        system_prompt = TRANSLATE_PROMPT.format(SOURCE_LANG=source_lang)
        user_prompt_json = {
            "positive_prompt": text1,
            "negative_prompt": text2
        }
        user_prompt = json.dumps(user_prompt_json, ensure_ascii=False)

        payload = {
            "model": config["model"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt }
            ],
            "temperature": 0
        }

        try:
            response = requests.post(
                f"{config['api_base'].rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            raw = result["choices"][0]["message"]["content"].strip()
            cleaned = re.sub(r"```json\n?|```", "", raw).strip()
            parsed = json.loads(cleaned)
            return (parsed.get("positive_translated", text1), parsed.get("negative_translated", text2))
        except Exception as e:
            print(f"[Translate Fail!: {e}]")
            return (text1, text2)

    def translate(self, positive_prompt, negative_prompt, source_lang="zh"):
        config = load_config()
        if not config.get("api_key"):
            return ("[NO API Key]", "[NO FOUND API Key]")

        translated_positive , translated_negative = self.llm_translate(positive_prompt, negative_prompt, config, source_lang)
        return (translated_positive, translated_negative)


NODE_CLASS_MAPPINGS = {
    "Translate(LLM)": TranslatePrompt
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Translate(LLM)": "Prompt翻訳(LLM)"
}

import os
import json
import requests

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "translate_config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "api_key": "",
        "model": "gemini-2.0-flash",
        "api_base": "https://generativelanguage.googleapis.com/v1beta/openai",
        "target_lang": "en",
        "system_prompt_zh": "你是一个专业的翻译助手，只返回翻译后的文本，不添加任何解释。",
        "user_prompt_zh": "请将以下文本翻译成{target_lang}：\n{text}"
    }

class TranslatePrompt:
    def __init__(self):
        self.FROM_LANG = "zh"
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "positive_prompt": ("STRING", {"multiline": True}),
                "negative_prompt": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("translated_positive", "translated_negative",)
    FUNCTION = "translate"
    CATEGORY = "utils"

    def gpt_translate(self, text, config):
        if not text.strip():
            return ""

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        user_prompt = config.get("user_prompt_" + self.FROM_LANG, "")
        user_prompt = user_prompt.replace('{target_lang}', config['target_lang'])
        user_prompt = user_prompt.replace('{text}', text)
        payload = {
            "model": config["model"],
            "messages": [
                {"role": "system", "content": f"{config['system_prompt_' + self.FROM_LANG]}"},
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
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"[Translate Fail!: {e}]"

    def translate(self, positive_prompt, negative_prompt):
        config = load_config()
        if not config.get("api_key"):
            return ("[NO API Key]", "[NO FOUND API Key]")

        translated_positive = self.gpt_translate(positive_prompt, config)
        translated_negative = self.gpt_translate(negative_prompt, config)
        return (translated_positive, translated_negative)


NODE_CLASS_MAPPINGS = {
    "Translate(LLM)": TranslatePrompt
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Translate(LLM)": "Prompt翻訳(LLM)"
}


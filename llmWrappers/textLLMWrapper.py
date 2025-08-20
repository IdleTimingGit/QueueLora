import os
import requests
from constants import *
from llmWrappers.abstractLLMWrapper import AbstractLLMWrapper



class TextLLMWrapper(AbstractLLMWrapper):
    def __init__(self, signals, tts, llmState, modules=None):
        super().__init__(signals, tts, llmState, modules)
        self.SYSTEM_PROMPT = SYSTEM_PROMPT
        self.LLM_ENDPOINT = LLM_ENDPOINT
        self.CONTEXT_SIZE = CONTEXT_SIZE
        # No tokenizer needed for Ollama API


    def prepare_payload(self):
        # Only include the system prompt if this is the first message in the conversation
        chat_prompt = self.generate_prompt()
        if len(self.signals.history) <= 2:  # 2 = system + first user message
            prompt = self.SYSTEM_PROMPT + "\n" + chat_prompt
        else:
            prompt = chat_prompt
        return {
            "model": MODEL,
            "prompt": prompt,
            "max_tokens": 200,
            "stop": STOP_STRINGS,
        }

    def generate_response(self):
        payload = self.prepare_payload()
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(f"{self.LLM_ENDPOINT}/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["text"]
        except Exception as e:
            print("[ERROR] LLM call failed:", e)
            return ""

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
        # Ollama OpenAI-compatible API expects a 'messages' list
        return {
            "model": MODEL,  # e.g., "llama3:8b"
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": self.generate_prompt()}
            ],
            "stream": False,  # Set to True if you want streaming
            "max_tokens": 200,
            "stop": STOP_STRINGS,
        }

    def generate_response(self):
        payload = self.prepare_payload()
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{self.LLM_ENDPOINT}/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        # Ollama returns choices[0]['message']['content']
        return data["choices"][0]["message"]["content"]
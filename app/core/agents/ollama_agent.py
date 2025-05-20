import os

from .base_agent import BaseAgent

from langchain_ollama import ChatOllama


class OllamaAgent(BaseAgent):

    def _get_chat_model(self):
        return ChatOllama(model=os.getenv("LLM_MODEL"), temperature=1.0)

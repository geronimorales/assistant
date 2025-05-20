import os

from .base_agent import BaseAgent

from langchain_openai import ChatOpenAI


class OpenAIAgent(BaseAgent):

    def _get_chat_model(self):
        return ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY", None),
            model=os.getenv("LLM_MODEL", "gpt-4o"),
            temperature=1.0
        )

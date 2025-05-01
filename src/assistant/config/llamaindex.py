from typing import Optional

from llama_index.core.multi_modal_llms import MultiModalLLM
from llama_index.core.settings import Settings

from assistant.config.app import config


# `Settings` does not support setting `MultiModalLLM`
# so we use a global variable to store it
_multi_modal_llm: Optional[MultiModalLLM] = None


def get_multi_modal_llm():
    return _multi_modal_llm


def init_settings():
    """Initialize LlamaIndex settings based on environment."""
    model_provider = config.get('llm.provider')
    match model_provider:
        case "openai":
            init_openai()
        case "ollama":
            init_ollama()


def init_ollama():
    """Initialize Ollama settings."""
    try:
        from llama_index.embeddings.ollama import OllamaEmbedding
        from llama_index.llms.ollama.base import DEFAULT_REQUEST_TIMEOUT, Ollama
    except ImportError:
        raise ImportError(
            "Ollama support is not installed. Please install it with `poetry add llama-index-llms-ollama` and `poetry add llama-index-embeddings-ollama`"
        )

    base_url = config.get('llm.ollama.host')
    request_timeout = float(config.get('llm.ollama.request_timeout'))
    Settings.embed_model = OllamaEmbedding(
        base_url=base_url,
        model_name=config.get('llm.ollama.embedding_model'),
    )
    Settings.llm = Ollama(
        base_url=base_url,
        model=config.get('llm.ollama.model'),
        request_timeout=request_timeout,
    )


def init_openai():
    """Initialize OpenAI settings."""
    from llama_index.core.constants import DEFAULT_TEMPERATURE
    from llama_index.embeddings.openai import OpenAIEmbedding
    from llama_index.llms.openai import OpenAI
    from llama_index.multi_modal_llms.openai import OpenAIMultiModal
    from llama_index.multi_modal_llms.openai.utils import GPT4V_MODELS

    max_tokens = config.get('llm.openai.max_tokens')
    model_name = config.get('llm.openai.model')
    Settings.llm = OpenAI(
        model=model_name,
        temperature=float(config.get('llm.openai.temperature') or DEFAULT_TEMPERATURE),
        max_tokens=int(max_tokens) if max_tokens is not None else None,
    )

    if model_name in GPT4V_MODELS:
        global _multi_modal_llm
        _multi_modal_llm = OpenAIMultiModal(model=model_name)

    dimensions = config.get('llm.openai.embedding_dimension')
    Settings.embed_model = OpenAIEmbedding(
        model=config.get('llm.openai.embedding_model'),
        dimensions=int(dimensions) if dimensions is not None else None,
    )


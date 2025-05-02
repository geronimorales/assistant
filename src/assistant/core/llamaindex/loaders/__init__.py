import logging
from typing import Any, Dict, List

import yaml  # type: ignore
from assistant.core.llamaindex.loaders.db import DBLoaderConfig, get_db_documents
from assistant.core.llamaindex.loaders.file import FileLoaderConfig, get_file_documents
from assistant.core.llamaindex.loaders.web import (
    WebLoaderConfig,
    get_web_documents,
    WebPageLoaderConfig,
    get_web_page_documents,
)
from llama_index.core import Document

logger = logging.getLogger(__name__)


def load_configs() -> Dict[str, Any]:
    with open("src/assistant/config/llamaindex/loaders.yaml") as f:
        configs = yaml.safe_load(f)
    return configs


def get_documents() -> List[Document]:
    """Load documents from the documents directory."""
    configs = load_configs()
    documents = []

    for loader_type, loader_config in configs.items():
        logger.info(
            f"Loading documents from loader: {loader_type}, config: {loader_config}"
        )
        match loader_type:
            case "file":
                document = get_file_documents(FileLoaderConfig(**loader_config))
            case "web":
                document = get_web_documents(WebLoaderConfig(**loader_config))
            case "web_pages":
                document = get_web_page_documents(WebPageLoaderConfig(**loader_config))
            case "db":
                document = get_db_documents(
                    configs=[DBLoaderConfig(**cfg) for cfg in loader_config]
                )
            case _:
                raise ValueError(f"Invalid loader type: {loader_type}")
        documents.extend(document)

    return documents

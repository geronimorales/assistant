import os
import logging
from typing import Dict, Optional
from llama_parse import LlamaParse
from pydantic import BaseModel
from llama_index.core.schema import Document
from llama_index.core.readers import SimpleDirectoryReader

from assistant.config.app import config as app_config

logger = logging.getLogger(__name__)


class FileLoaderConfig(BaseModel):
    use_llama_parse: bool = False


def llama_parse_parser():
    if os.getenv("LLAMA_CLOUD_API_KEY") is None:
        raise ValueError(
            "LLAMA_CLOUD_API_KEY environment variable is not set. "
            "Please set it in .env file or in your shell environment then run again!"
        )
    parser = LlamaParse(
        result_type="markdown",
        verbose=True,
        language="en",
        ignore_errors=False,
    )
    return parser


def llama_parse_extractor() -> Dict[str, LlamaParse]:
    from llama_parse.utils import SUPPORTED_FILE_TYPES

    parser = llama_parse_parser()
    return {file_type: parser for file_type in SUPPORTED_FILE_TYPES}


def get_file_documents(config: FileLoaderConfig, dir_path: str | None = None):
    try:
        file_extractor = None
        if config.use_llama_parse:
            # LlamaParse is async first,
            # so we need to use nest_asyncio to run it in sync mode
            import nest_asyncio

            nest_asyncio.apply()

            file_extractor = llama_parse_extractor()
        reader = SimpleDirectoryReader(
            dir_path or app_config.get("llamaindex.data_dir"),
            recursive=True,
            filename_as_id=True,
            raise_on_error=True,
            file_extractor=file_extractor,
        )
        return reader.load_data()
    except Exception as e:
        import sys
        import traceback

        # Catch the error if the data dir is empty
        # and return as empty document list
        _, _, exc_traceback = sys.exc_info()
        function_name = traceback.extract_tb(exc_traceback)[-1].name
        if function_name == "_add_files":
            logger.warning(
                f"Failed to load file documents, error message: {e} . Return as empty document list."
            )
            return []
        else:
            # Raise the error if it is not the case of empty data dir
            raise e


def get_document(
    file_path: str,
    metadata: Optional[Dict] = None,
    use_llama_parse: bool = False
) -> Document:
    """
    Process a single file and return it as a Document.
    
    Args:
        file_path: Path to the file to process
        metadata: Optional metadata to add to the document
        use_llama_parse: Whether to use LlamaParse for processing
    
    Returns:
        Document: A llama_index Document containing the file content
    """
    try:
        # Configure the file loader
        config = FileLoaderConfig(use_llama_parse=use_llama_parse)
        
        # Create a SimpleDirectoryReader for the single file
        file_extractor = None
        if config.use_llama_parse:
            import nest_asyncio
            nest_asyncio.apply()
            file_extractor = llama_parse_extractor()
            
        reader = SimpleDirectoryReader(
            input_files=[file_path],
            filename_as_id=True,
            raise_on_error=True,
            file_extractor=file_extractor,
        )
        
        # Load the document
        documents = reader.load_data()
        
        if not documents:
            raise ValueError(f"No documents were extracted from the file: {file_path}")
        
        # Get the first document
        document = documents[0]
        
        # Add additional metadata if provided
        if metadata:
            document.metadata.update(metadata)
        
        return document
        
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        raise

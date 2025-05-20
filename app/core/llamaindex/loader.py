from pathlib import Path
from typing import List

from llama_index.core import Document
from llama_index.readers.file import SimpleDirectoryReader


def get_documents(dir_path: str) -> List[Document]:
    """Load documents from the documents directory."""
    documents_dir = Path(dir_path)
    if not documents_dir.exists():
        raise FileNotFoundError(f"Documents directory not found: {documents_dir}")

    reader = SimpleDirectoryReader(
        input_dir=str(documents_dir),
        recursive=True,
        exclude_hidden=True,
    )
    return reader.load_data()

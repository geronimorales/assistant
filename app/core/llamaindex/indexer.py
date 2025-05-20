from app.config.app import config
from sqlalchemy import make_url
from llama_index.core import StorageContext
from llama_index.vector_stores.postgres import PGVectorStore

from app.db.base import get_database_url

from app.core.llamaindex.loaders import load_documents_from_dir
from app.core.llamaindex.loaders.file import get_file_document
from app.config.llamaindex import init_settings

from llama_index.core.indices import VectorStoreIndex

from app.repositories.file_chunk import FileChunkRepository

def get_vector_store():
    """Get or create the vector store instance."""
    embed_dim = 768
    table_name = config.get("llamaindex.data_table")

    url = make_url(get_database_url())

    return PGVectorStore.from_params(
        database=url.database,
        host=url.host,
        password=url.password,
        port=str(url.port) if url.port else None,
        user=url.username,
        table_name=table_name,
        embed_dim=embed_dim,
        hnsw_kwargs={
            "hnsw_m": 16,
            "hnsw_ef_construction": 64,
            "hnsw_ef_search": 40,
            "hnsw_dist_method": "vector_cosine_ops",
        },
    )

async def index_file_documents(dir_path: str, metadata: dict = {}):
    init_settings()

    vector_store = get_vector_store()

    if "event_id" in metadata:
        event_id = metadata.get("event_id")
        file_chunk_repository = FileChunkRepository()
        await file_chunk_repository.delete_by_metadata("event_id", event_id)

    # load the documents and create the index
    documents = load_documents_from_dir(dir_path)

    # llama index filters documents with private=true
    # so we need to set private=false for the documents
    # if we don't set this metadata key the documents will be ignored
    # when we query the index
    for doc in documents:
        doc.metadata["private"] = "false"        
        for key, value in metadata.items():
            doc.metadata[key] = value

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, show_progress=True
    )

async def index_file_document(file_path: str, metadata: dict = None):
    """
    Index a single document from a file path.
    
    Args:
        file_path: Path to the file to index
        metadata: Optional metadata to add to the document
    
    Returns:
        The created VectorStoreIndex
    """
    init_settings()
    
    # Get the document
    document = get_file_document(file_path, metadata=metadata)
    
    # Set private flag to false to ensure document is queryable
    document.metadata["private"] = "false"
    
    # Get vector store
    vector_store = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Create index from single document
    index = VectorStoreIndex.from_documents(
        [document],
        storage_context=storage_context,
        show_progress=True
    )
    
    return index

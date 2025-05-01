from assistant.config.app import config
from sqlalchemy import make_url
from llama_index.core import StorageContext
from llama_index.vector_stores.postgres import PGVectorStore

from assistant.config.database import get_database_url

from assistant.core.llamaindex.loaders import get_documents
from assistant.config.llamaindex import init_settings

from llama_index.core.indices import VectorStoreIndex


def generate():
    init_settings()

    embed_dim = 768
    table_name = config.get('llamaindex.data_table')

    url = make_url(get_database_url())

    vector_store = PGVectorStore.from_params(
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

    # load the documents and create the index
    documents = get_documents()

    # llama index filters documents with private=true
    # so we need to set private=false for the documents
    # if we don't set this metadata key the documents will be ignored
    # when we query the index
    for doc in documents:
        doc.metadata["private"] = "false"

    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context, 
        show_progress=True
    )

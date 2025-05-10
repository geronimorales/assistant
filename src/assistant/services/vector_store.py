from assistant.config.llamaindex import init_settings

from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.postgres import PGVectorStore
from sqlalchemy import make_url

from assistant.config.app import config
from assistant.db.base import get_database_url


class VectorStoreService:
    """Service for managing vector store operations."""

    def __init__(self):
        init_settings()
        self.vector_store = self._create_vector_store()

    def _create_vector_store(self) -> PGVectorStore:
        """Create a PostgreSQL vector store."""
        url = make_url(get_database_url())
        return PGVectorStore.from_params(
            database=url.database,
            host=url.host,
            password=url.password,
            port=str(url.port) if url.port else None,
            user=url.username,
            table_name=config.get("llamaindex.data_table"),
            embed_dim=768,  # TODO: Make this configurable
            hnsw_kwargs={
                "hnsw_m": 16,
                "hnsw_ef_construction": 64,
                "hnsw_ef_search": 40,
                "hnsw_dist_method": "vector_cosine_ops",
            },
        )

    def get_index(self) -> VectorStoreIndex:
        """Get the vector store index."""
        return VectorStoreIndex.from_vector_store(vector_store=self.vector_store)

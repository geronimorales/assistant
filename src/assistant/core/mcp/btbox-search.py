import requests
import uuid
from datetime import datetime, timedelta
from typing import Literal, Optional
from mcp.server.fastmcp import FastMCP
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter
from assistant.services.vector_store import VectorStoreService

mcp = FastMCP("Btbox Search")

@mcp.tool()
def list_coincidences(query: str, user_data: Optional[dict] = None) -> dict:
    """Retrieves documents with information of persons that match with the given query

    Args:
        query: The query to search for.

    Returns:
        A dict with the documents retrieved from the vector store.
    """
    if not "user_config_id" in user_data:
        raise ValueError("user_config_id is not present in user_data")            
    retriever = _get_retriever(max_items=10, metadata={
        "user_config_id": user_data["user_config_id"]
    })
    docs = retriever.retrieve(query)
    results = [doc.node.get_content() for doc in docs]
    return {"coincidences": results}

def _get_retriever(max_items: int = 5, metadata: Optional[dict] = None) -> BaseRetriever:
    vector_store = VectorStoreService()
    index = vector_store.get_index()

    filters = []
    for k, v in metadata.items():
        filters.append(MetadataFilter(key=k, value=v))

    return index.as_retriever(
        similarity_top_k=max_items,
        filters=MetadataFilters(
            filters=filters
        ),
    )
 
if __name__ == "__main__":
    mcp.run(transport="stdio")

from typing import List

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.vector_store import VectorStoreService


router = APIRouter(tags=["search"])


class SearchQuery(BaseModel):
    query: str
    limit: int = 5


class SearchResult(BaseModel):
    content: str
    metadata: dict
    score: float


@router.post("/search", response_model=List[SearchResult])
async def search(query: SearchQuery) -> List[SearchResult]:
    """Search documents using vector similarity."""
    vector_store = VectorStoreService()
    index = vector_store.get_index()
    query_engine = index.as_query_engine()
    response = await query_engine.aquery(query.query)
    return [
        SearchResult(
            content=node.node.text,
            metadata=node.node.metadata,
            score=node.score,
        )
        for node in response.source_nodes
    ]

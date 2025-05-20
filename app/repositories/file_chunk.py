from typing import List, Optional

from sqlalchemy import select, func, delete, cast, String, Integer

from app.models.file_chunk import FileChunk
from app.repositories.base import BaseRepository
from app.schemas.file_chunk import FileChunkBase, FileChunkInDB

class FileChunkRepository(BaseRepository[FileChunk, FileChunkBase, FileChunkInDB]):
    """Repository for managing FileChunk entities."""
    
    def __init__(self):
        super().__init__(FileChunk)

    async def get_by_node_id(self, node_id: str) -> Optional[FileChunk]:
        """Get a file chunk by its node_id."""
        async with self.session as session:
            result = await session.execute(
                select(FileChunk).where(FileChunk.node_id == node_id)
            )
            return result.scalar_one_or_none()
    
    async def get_by_metadata(self, metadata_key: str, metadata_value: str) -> List[FileChunk]:
        """Get file chunks by metadata key-value pair."""
        async with self.session as session:
            result = await session.execute(
                select(FileChunk).where(
                    FileChunk.metadata_[metadata_key].astext == metadata_value
                )
            )
            return result.scalars().all()
        
    async def delete_by_metadata(self, metadata_key: str, metadata_value: str) -> None:
        """Delete file chunks by metadata key-value pair."""
        session = await self.session
        async with session as s:
            await s.execute(
                delete(FileChunk).where(
                    cast(FileChunk.metadata_.op("->>")(metadata_key), Integer) == metadata_value
                )
            )
            await s.commit()

    async def find_similar(
        self,
        embedding: List[float],
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[FileChunk]:
        """
        Find similar chunks using cosine similarity.
        
        Args:
            embedding: The embedding vector to compare against
            limit: Maximum number of results to return
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of similar FileChunks ordered by similarity
        """
        async with self.session as session:
            # Using cosine similarity (1 - cosine_distance)
            result = await session.execute(
                select(
                    FileChunk,
                    (1 - func.cosine_distance(FileChunk.embedding, embedding)).label('similarity')
                )
                .where(FileChunk.embedding.isnot(None))
                .order_by(func.cosine_distance(FileChunk.embedding, embedding))
                .limit(limit)
            )
            
            # Filter by similarity threshold and return only the chunks
            chunks = []
            for chunk, similarity in result:
                if similarity >= similarity_threshold:
                    chunks.append(chunk)
            
            return chunks 
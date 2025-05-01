import requests
import uuid
from typing import Literal
from mcp.server.fastmcp import FastMCP
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter
from assistant.services.vector_store import VectorStoreService

mcp = FastMCP("Btbox MCP")

api_key = ""

@mcp.tool()
def list_coincidences(query: str) -> dict:
    """Retrieves documents with information of persons that match with the given query
    
    Args:
        query: The query to search for.

    Returns:
        A dict with the documents retrieved from the vector store.
    """
    retriever = _get_retriever()

    docs = retriever.retrieve(query)
    
    return {"coincidences": docs}

@mcp.tool()
def get_user_account() -> dict:
    """Retrieves account information of the active user.

    Returns:
        A dict with the user account information.
    """
    return {
        "id": 13,
        "name": "Luciano Genessini",
        "email": "lucianogenessini@gmail.com",
        "phone": "+543938439384",
        "address": "123 Main St, Anytown, USA",
    }

@mcp.tool()
def get_user_calendar(user_id: int) -> dict:
    """Retrieves the user's calendar with free time slots

    Args:
        user_id: The id of the user to get the calendar.

    Returns:
        A dict with the meetings.
    """
    return {"calendar": [
        {
            "id": uuid.uuid4(),
            "date": "2024-01-01",
            "time": "09:00",
        },
        {
            "id": uuid.uuid4(),
            "date": "2024-01-01",
            "time": "09:30",
        },
        {
            "id": uuid.uuid4(),
            "modality": "in_person",
            "date": "2024-01-01",
            "time": "10:00",
            "duration": 30,
            "title": "Reunión con Mauricio Nudelman",
            "participants": 2,
        },
        {
            "id": uuid.uuid4(),
            "date": "2024-01-01",
            "time": "10:30",
        },
        {
            "id": uuid.uuid4(),
            "date": "2024-01-01",
            "time": "11:00",
        },
        {
            "id": uuid.uuid4(),
            "date": "2024-01-01",
            "time": "11:30",
        }, 
        {
            "id": uuid.uuid4(),
            "date": "2024-01-01",
            "time": "12:00",
        },
    ]}

@mcp.tool()
def create_meeting(
    modality: Literal["in_person", "virtual"],
    date: str, 
    time: str, 
    duration: int,
    title: str,
    participant_ids: list[int]
) -> dict:
    """Creates a meeting with the given date, time and participants

    Args:
        modality: The modality of the meeting (in_person, virtual).
        date: The date of the meeting in format YYYY-MM-DD.
        time: The time of the meeting in format HH:MM.
        duration: The duration of the meeting in minutes.
        title: The title of the meeting.
        participant_ids: The ids of the participants.

    Returns:
        A dict with the meeting information.
    """
    return {
        "id": uuid.uuid4(),
        "modality": modality,
        "date": date,
        "time": time,
        "duration": duration,
        "title": title,
        "participants": len(participant_ids)
    }

def _get_retriever(max_items: int = 5) -> BaseRetriever:
    vector_store = VectorStoreService()
    index = vector_store.get_index()
    return index.as_retriever(
        similarity_top_k=max_items,
        filters=MetadataFilters(
            filters=[MetadataFilter(key="file_name", value="btbox.xlsx")]
        ),
    )

def _exchange_token() -> str:
    """Exchange the token for a new one.

    Returns:
        A new token.
    """
    pass
    # response = requests.get(f"{api_url}/datum-os/oauth/token/exchange", headers=_headers())
    # response.raise_for_status()
    # return response.json()["access_token"]

def _headers(token=None) -> dict:
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")
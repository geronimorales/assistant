import requests
import uuid
from datetime import datetime, timedelta
from typing import Literal, Optional
from mcp.server.fastmcp import FastMCP
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter
from assistant.services.vector_store import VectorStoreService

mcp = FastMCP("Btbox MCP")

server_url = "https://admin-dev.btboxevolution.com/api/assistant-chat"

api_key = "NuTrd1ZNlKHfqGCQG4yDwkTRlgFS188p"


@mcp.tool()
def list_coincidences(query: str, user_data: Optional[dict] = None) -> dict:
    """Retrieves documents with information of persons that match with the given query

    Args:
        query: The query to search for.

    Returns:
        A dict with the documents retrieved from the vector store.
    """

    metadata = {}

    if "event_id" in user_data:
        metadata["event_id"] = user_data["event_id"]

    retriever = _get_retriever(max_items=10, metadata=metadata)

    docs = retriever.retrieve(query)

    results = [doc.node.get_content() for doc in docs]

    return {"coincidences": results}


@mcp.tool()
def get_user_account(user_data: Optional[dict] = None) -> dict:
    """Retrieves account information of the active user.

    Returns:
        A dict with the user account information.
    """
    response = requests.get(
        f"{server_url}/user", 
        headers=_headers(),
        json={
            "user_id": user_data.get("user_id", None),
            "event_id": user_data.get("event_id", None)
        }
    )   
    return _response_data(response)
    

@mcp.tool()
def get_users_calendar(
    current_user_id: int,
    invited_user_id: int,
    user_data: Optional[dict] = None
) -> dict:
    """Retrieves the calendar of the user with the given id

    Args:
        current_user_id: The id of the current user.
        invited_user_id: The id of the invited user.

    Returns:
        A dict with calendar information for both users.
    """
    response = requests.get(
        f"{server_url}/calendar", 
        headers=_headers(),
        json={
            "applicant_id": current_user_id,
            "counterpart_id": invited_user_id,
            "event_id": user_data.get("event_id", None)
        }
    )   
    data = _response_data(response)
    
    return data

@mcp.tool()
def create_meeting(
    modality: Literal["in_person", "virtual"],
    date: str,
    time: str,
    title: str,
    current_user_id: int,
    invited_user_id: int,
    user_data: Optional[dict] = None
) -> dict:
    """Creates a meeting with the given data

    Args:
        modality: The modality of the meeting (in_person, virtual).
        date: The date of the meeting in format YYYY-MM-DD.
        time: The time of the meeting in format HH:MM.
        title: The title of the meeting.
        current_user_id: The id of the current user.
        invited_user_id: The id of the invited user.

    Returns:
        A dict with the meeting information.
    """
    params = {
        "applicant_id": current_user_id,
        "counterpart_id": invited_user_id,
        "event_id": user_data.get("event_id", None),
        "meeting_type": 1 if modality == "virtual" else 2,
        "meeting_date": f"{date} {time}:00",
    }

    params_str = "&".join([f"{k}={v}" for k, v in params.items()])

    response = requests.post(
        f"{server_url}/meetings?{params_str}", 
        headers=_headers()
    )  
    return _response_data(response) | {
        "title": title, 
        "duration": 30 + 10
    }

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

def _headers(token=None) -> dict:
    return {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
    }

def _response_data(response: requests.Response) -> dict:
    response.raise_for_status()
    content = None
    try:
        content = response.json()
    except Exception as e: 
        print("Error parsing response: ", e)
        content = {}
    finally:
        return content.get("data", {})
    
if __name__ == "__main__":
    mcp.run(transport="stdio")

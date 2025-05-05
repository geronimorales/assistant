import requests
import uuid
from datetime import datetime, timedelta
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
    retriever = _get_retriever(max_items=10)

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
def get_users_calendar(current_user_id: int, invited_user_id: int) -> dict:
    """Retrieves the calendar of the user with the given id

    Args:
        current_user_id: The id of the current user.
        invited_user_id: The id of the invited user.

    Returns:
        A dict with calendar information for both users.
    """
    # Generate dates starting from tomorrow
    start_date = datetime.now() + timedelta(days=1)

    print("Start date: ", start_date)
    dates = {}
    
    # Generate 3 days of calendar data
    for i in range(3):
        date = start_date + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        # Generate some random blocked slots for demonstration
        blocked_slots = []
        if i == 0:  # First day
            blocked_slots = ["09:20", "09:40", "11:00"]
        elif i == 1:  # Second day
            blocked_slots = ["09:00", "09:20", "09:40", "10:00", "10:20", "10:40", "11:00", "11:20", "11:40"]
        elif i == 2:  # Third day
            blocked_slots = ["10:00"]
            
        dates[date_str] = {
            "blocked": blocked_slots
        }

    return {
        "calendar": {
            "start_at": "09:00",
            "end_at": "18:00",
            "duration": 20,  
            "dates": dates
        }
    }

@mcp.tool()
def create_meeting(
    modality: Literal["in_person", "virtual"],
    date: str,
    time: str,
    title: str,
    current_user_id: int,
    invited_user_id: int,
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
    return {
        "id": uuid.uuid4(),
        "modality": modality,
        "date": date,
        "time": time,
        "duration": 20,
        "title": title,
        "current_user_id": current_user_id,
        "invited_user_id": invited_user_id,
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


def generate_time_slots():
    """Generate time slots from 8 AM to 12 PM in 20-minute intervals."""
    slots = []
    for hour in range(8, 12):
        for minute in range(0, 60, 20):
            time = f"{hour:02d}:{minute:02d}"
            slots.append(time)
    return slots

def generate_calendar():
    """Generate a calendar dictionary for the next 7 days with time slots."""
    current_date = datetime.now()
    calendar = {}
    
    # Generate time slots
    time_slots = generate_time_slots()
    
    # Generate calendar for next 7 days
    for day in range(7):
        date = current_date + timedelta(days=day)
        date_str = date.strftime("%Y-%m-%d")
        calendar[date_str] = {
            "slots": time_slots,
            "available": {slot: True for slot in time_slots}
        }
    
    return calendar

if __name__ == "__main__":
    mcp.run(transport="stdio")

import requests
from typing import Literal, Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Btbox Meetings")

server_url = ""

api_key = "NuTrd1ZNlKHfqGCQG4yDwkTRlgFS188p"

@mcp.tool()
def get_user_info(user_data: Optional[dict] = None) -> dict:
    """Retrieves account information of the active user.

    Returns:
        A dict with the user account information.
    """
    server_url = _api_url(user_data)
    response = requests.get(
        f"{server_url}/assistant-chat/user", 
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
    server_url = _api_url(user_data)
    response = requests.get(
        f"{server_url}/assistant-chat/calendar", 
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

    server_url = _api_url(user_data)

    params = {
        "applicant_id": current_user_id,
        "counterpart_id": invited_user_id,
        "event_id": user_data.get("event_id", None),
        "meeting_type": 1 if modality == "virtual" else 2,
        "meeting_date": f"{date} {time}:00",
    }

    params_str = "&".join([f"{k}={v}" for k, v in params.items()])

    response = requests.post(
        f"{server_url}/assistant-chat/meetings?{params_str}", 
        headers=_headers()
    )  
    return _response_data(response) | {
        "title": title, 
        "duration": user_data.get("duration", 30),
        "break_time": user_data.get("break_time", 10)
    }

def _api_url(user_data: dict) -> str:
    if "api_url" not in user_data:
        raise ValueError("api_url is not present in user_data")
    return user_data.get("api_url")

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

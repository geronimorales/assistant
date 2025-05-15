import json
from typing import Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Form, APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from assistant.config.app import config
from assistant.config.mcp import load_config
from assistant.repositories.thread import ThreadRepository

from assistant.core.agents.openai_agent import OpenAIAgent

router = APIRouter()
thread_repository = ThreadRepository()


@router.post("/assistant/init")
async def init(
    payload: Optional[Dict] = None,
) -> Dict[str, str]:
    """Initialize a new thread with optional user data."""
    
    try:
        user_data = payload.get("user_data", None)
    except:
        user_data = None
    
    thread = await thread_repository.create_with_user_data(user_data=user_data)
    return {"thread_id": str(thread.id)}


@router.post(
    "/assistant/chat",
    summary="Receives a message from user along with a thread_id and returns the assistant's response.",
)
async def chat(message: str = Form(...), thread_id: str = Form(...)):
    try:
        thread = await thread_repository.get_by_id(thread_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found"
        )

    mcps = config.get("llm.mcp.servers")

    mcp_configs = {}

    all_mcp_configs = load_config()
    for mcp_server in mcps:
        mcp_configs[mcp_server] = all_mcp_configs[mcp_server]

    agent = OpenAIAgent(
        thread_id=thread.id, 
        mcps=mcp_configs,
        user_data=thread.user_data
    )

    response = agent.stream(message)

    return StreamingResponse(response, media_type="text/event-stream")

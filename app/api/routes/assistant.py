import json
from typing import Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Form, Body, HTTPException, status
from fastapi.responses import StreamingResponse

from app.config.app import config
from app.config.mcp import load_config
from app.repositories.thread import ThreadRepository
from app.schemas.thread import Thread, ThreadCreate

from app.core.agents.openai_agent import OpenAIAgent
from app.core.agents import prompts
from pydantic import BaseModel
from typing import Optional, Dict
from app.repositories.user_config import UserConfigRepository

router = APIRouter()
user_config_repository = UserConfigRepository()
thread_repository = ThreadRepository()
    
@router.post("/assistant/init", response_model=Optional[Thread])
async def init(
    data: ThreadCreate = Body(...),
) -> Optional[Thread]:
    """Initialize a new thread with optional user data."""    
    try:

        user_config = await user_config_repository.get_by_id(data.user_config_id)
        if not user_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User config is not valid"
            )

        # Get user data from request and prevent saving keys present in user_config
        user_data = data.user_data or {}
        not_allowed_keys = [k for k, _ in user_config.config.items()]
        filtered_user_data = {k:v for k, v in user_data.items() if k not in not_allowed_keys}
        
        thread = await thread_repository.create_with_config(
            user_config_id=data.user_config_id,
            user_data=filtered_user_data
        )
        
        return thread
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Can't init thread: {e}"
        )

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

    user_data = {"user_config_id": str(thread.user_config.id)} | thread.user_data | thread.user_config.config

    print("user_data", user_data)

    agent = OpenAIAgent(
        thread_id=thread.id, 
        prompt=prompts.BTBOX_PROMPT,
        mcps=mcp_configs,
        user_data=user_data
    )

    response = agent.stream(message)

    return StreamingResponse(response, media_type="text/event-stream")

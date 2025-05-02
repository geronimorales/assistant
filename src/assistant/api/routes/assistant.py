import uuid

from fastapi import APIRouter, Form, APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from assistant.config.app import config

from assistant.config.mcp import load_config

from assistant.core.agents.ollama_agent import OllamaAgent
from assistant.core.agents.openai_agent import OpenAIAgent

router = APIRouter()


@router.post(
    "/assistant/init",
    summary="Creates a thread_id to keep track of a new conversation",
    description="Returns a thread_id",
)
async def init():
    thread_id = str(uuid.uuid4())
    if not thread_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Thread not created"
        )
    return {"thread_id": thread_id}


@router.post(
    "/assistant/chat",
    summary="Receives a message from user along with a thread_id and returns the assistant's response.",
)
async def chat(message: str = Form(...), thread_id: str = Form(...)):

    if not thread_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found"
        )

    mcps = config.get("llm.mcp.servers")

    mcp_configs = {}

    all_mcp_configs = load_config()
    for mcp_server in mcps:
        mcp_configs[mcp_server] = all_mcp_configs[mcp_server]

    agent = OpenAIAgent(thread_id, mcps=mcp_configs)

    response = agent.stream(message)

    return StreamingResponse(response, media_type="text/event-stream")

from fastapi import APIRouter
from app.config.app import config

router = APIRouter()


@router.get(
    "/",
    summary="Get information from the knowledge base",
    description="Retrieves relevant information from the knowledge base based on the provided search query. Returns a text response containing the matched information.",
)
async def home_request():
    return {
        "message": "Welcome to AI Assistant API",
        "version": config.get("api.version"),
        "environment": config.get("app.env"),
    }

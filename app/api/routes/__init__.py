"""This module is used to define the API routers."""

from fastapi import APIRouter

from app.api.routes import (
    assistant, 
    search, 
    home, 
    files
)

api_router = APIRouter()
api_router.include_router(assistant.router)
api_router.include_router(home.router)
api_router.include_router(search.router)
api_router.include_router(files.router)
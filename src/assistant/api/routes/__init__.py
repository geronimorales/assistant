"""This module is used to define the API routers."""

from fastapi import APIRouter

from assistant.api.routes import (
    assistant,
    search,
    home
)

api_router = APIRouter()
api_router.include_router(assistant.router)
api_router.include_router(home.router)
api_router.include_router(search.router)
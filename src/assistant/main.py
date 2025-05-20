from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from assistant.config.app import config
from assistant.api.routes import api_router

def create_app() -> FastAPI:
    app = FastAPI(
        title=config.get("api.title"),
        version=config.get("api.version"),
        debug=config.get("app.debug"),
    )

    # Configure CORS
    if config.get("app.env") == "local":
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.get("cors.origins"),
            allow_credentials=True,
            allow_methods=config.get("cors.methods"),
            allow_headers=config.get("cors.headers"),
        )

    # Include routers
    app.include_router(api_router, prefix=config.get("api.prefix"))

    return app

app = create_app()

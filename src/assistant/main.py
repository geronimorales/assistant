from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from assistant.core.settings import settings

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


print("Starting AI Assistant API", settings.API_TITLE, settings.OPENAI_API_KEY)

# Include routers
@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Assistant API",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT
    } 
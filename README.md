# AI Assistant Project

This project is a FastAPI-based AI assistant that uses LangChain, LangGraph, and LlamaIndex for AI capabilities, with PostgreSQL as the database.

## Prerequisites

- Python 3.9 or higher
- Poetry for dependency management
- PostgreSQL database

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   poetry install
   ```

3. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file with your actual configuration values.

4. Initialize the database:
   ```bash
   poetry run alembic upgrade head
   ```

## Running the Application

To run the application in development mode:

```bash
poetry run uvicorn assistant.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:
- Swagger UI documentation at `http://localhost:8000/docs`
- ReDoc documentation at `http://localhost:8000/redoc`

## Project Structure

```
assistant/
├── src/
│   └── assistant/
│       ├── api/        # API routes and endpoints
│       ├── core/       # Core configuration and settings
│       ├── db/         # Database models and configuration
│       ├── models/     # Pydantic models
│       └── services/   # Business logic and services
├── migrations/         # Database migrations
├── tests/             # Test files
├── pyproject.toml     # Poetry configuration
└── alembic.ini        # Alembic configuration
``` 
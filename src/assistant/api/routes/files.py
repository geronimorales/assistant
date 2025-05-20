import json
import tempfile
import shutil
from pathlib import Path
from uuid import UUID
from typing import Dict, Optional

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from assistant.core.llamaindex.indexer import index_file_documents
from assistant.repositories.user_config import UserConfigRepository
router = APIRouter()


@router.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_config_id: str = Form(None),
) -> JSONResponse:
    """
    Upload a file with optional metadata. Index the file and return a JSON response.
    
    Args:
        file: The file to upload
        user_config_id: identifier for the user config to use
    
    Returns:
        JSONResponse with file details and metadata
    """

    temp_dir = None
    user_data = None

    try: 
        # Load user config if provided
        user_config_repo = UserConfigRepository()
        user_config = await user_config_repo.get_by_id(
            config_id=UUID(user_config_id)
        )
        if not user_config:
            return JSONResponse(
                content={"error": "User config not found"},
                status_code=404
            )

        temp_dir = tempfile.mkdtemp()            
        
        temp_dir_path = Path(temp_dir)
        temp_file_path = temp_dir_path / file.filename
        print("temp_file_path", temp_file_path)
        with open(temp_file_path, "wb") as f:
            # Read chunks to handle large files
            for chunk in file.file:
                f.write(chunk)

        metadata = {"user_config_id": user_config_id}

        await index_file_documents(dir_path=temp_dir_path, metadata=metadata)

        return JSONResponse(
            content={"message": "File uploaded and indexed successfully"},
            status_code=200
        )
    except Exception as e:
        print("Error", e)
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )            
    finally:
        # Clean up - remove temp directory and contents
        if temp_dir:
            shutil.rmtree(temp_dir)

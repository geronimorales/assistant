import json
import tempfile
import shutil
from pathlib import Path

from typing import Dict, Optional

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from assistant.core.llamaindex.indexer import index_file_documents

router = APIRouter()


@router.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    payload: Optional[str] = Form(None),
) -> JSONResponse:
    """
    Upload a file with optional metadata. Index the file and return a JSON response.
    
    Args:
        file: The file to upload
        payload: Optional dictionary containing metadata about the file
    
    Returns:
        JSONResponse with file details and metadata
    """

    temp_dir = None
    user_data = None

    print("payload", payload)

    try: 
        payload =  json.loads(payload)    
        user_data = payload.get("user_data", None)
    except Exception as e:
        print("Error loading json: ", e)
        user_data = None
           
    try:

        temp_dir = tempfile.mkdtemp()            
        
        temp_dir_path = Path(temp_dir)
        temp_file_path = temp_dir_path / file.filename
        print("temp_file_path", temp_file_path)
        with open(temp_file_path, "wb") as f:
            # Read chunks to handle large files
            for chunk in file.file:
                f.write(chunk)

        index_file_documents(dir_path=temp_dir_path, metadata=user_data)

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

from typing import Dict, Optional

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    payload: Optional[Dict] = Form(None),
) -> JSONResponse:
    """
    Upload a file with optional metadata.
    
    Args:
        file: The file to upload
        payload: Optional dictionary containing metadata about the file
    
    Returns:
        JSONResponse with file details and metadata
    """
    try:
        # Read file content
        content = await file.read()
        
        # Create response with file details
        response = {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content),
            "metadata": payload or {}
        }
        
        return JSONResponse(
            content=response,
            status_code=200
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
    finally:
        await file.close() 
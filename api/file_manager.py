from fastapi import (
    File, 
    UploadFile, 
    APIRouter, 
    BackgroundTasks, 
    HTTPException, 
    Query, 
    Path, 
)

import json
from pdfminer.high_level import extract_text
from api.supa import UserState, supa, SupaSession
from urllib.parse import unquote
from sqlmodel import select
from typing import Annotated
from api.models import Document


# app = FastAPI()
app = APIRouter(
    prefix="/p/file",
    tags=["file"],
)


@app.post("/upload")
async def upload_file(file: UploadFile, user:UserState, background_tasks: BackgroundTasks, session:SupaSession):

    file_content = file.file.read()
    
    # Upload file to storage
    res = supa.storage.from_("files").upload(
        f"{user.id}/{file.filename}",    
        file_content    ,        
        {"content-type": file.content_type},)
    
    # check if file is uploaded
    stored_file = json.loads(res.content.decode("utf-8"))  
    
    print(stored_file)
       
    if not stored_file:
        raise HTTPException(status_code=400, detail="Failed to upload file")

    new_documet = Document(
        name=file.filename,
        storage_object_id=stored_file["Id"],
        size=file.size,
        type=file.content_type,
        created_by=user.id,
    )
    session.add(new_documet)
    session.commit()
    session.refresh(new_documet)
    
    print(new_documet)
    
    
    return {
        "status": "success",
        "message": "File uploaded successfully"
    }

@app.get("/list", response_model=list[Document], response_model_exclude_unset=True, response_model_exclude=["storage_object_id"])
async def lists_files(
    session : SupaSession, 
    user    : UserState, 
    offset  : Annotated[int, Query(
        title="start from:",
        description="Query string for the items to search in the database that have a good match",
        ge=0
    )] = 0, 
    limit   : Annotated[int, Query(ge=1, le=50)] = 10
    ):
    return  session.exec(
                select(Document).
                where(Document.created_by == user.id).
                offset(offset).limit(limit)
            ).all()
  
    
@app.get("/get/{filename}")
async def get_file(filename:Annotated[str,Path(title="Path to the file")],user: UserState):
    # decode filename from url
    decoded_file_name = unquote(filename)
    file_path = f"{user.id}/{decoded_file_name}"
    
    print(file_path)
    
    return {
        'url': supa.storage.from_("files").create_signed_url(file_path, 60)
    }



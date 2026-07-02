from fastapi import APIRouter, BackgroundTasks, Depends,File, Form, UploadFile
from rag_redis.pdfParser.parser import PDFParser
from rag_redis.chuncker.main import Chuncker
from rag_redis.chromaDB import ChromaDB
from sse_starlette.sse import EventSourceResponse
from asyncio import to_thread,sleep
from uuid import uuid4
from services.supabase_service import SupabaseDB
import json
from pathlib import Path

UPLOAD_DIR = Path("uploads")

upload_router = APIRouter(
     prefix="/upload",
    tags=["Upload"]
)

jobs = {}

def get_db():
     db = SupabaseDB()
     return db

async def process_pdf(url: str, job_id : str, db : object, doc_id : str, userid: str):
    jobs[job_id]['status'] = "Starting parser"
    
    
    parser = PDFParser(url)
    cleaned_pages = await to_thread(parser.cleanup)
    

    print("Parsed")
    jobs[job_id]['status'] ="Pdf Parsed"

    chunker = Chuncker(cleaned_pages)
    chunks = await to_thread(chunker.chunk_pages)
    
    print("Chunked")
    jobs[job_id]['status'] = "pdf Chucked"

    chroma = ChromaDB("rag-collection")
    await to_thread(chroma.embedding, chunks, userid=userid)
    await to_thread(db.update_document_status,doc_id, "Indexed")
    
    print("Indexed")
    jobs[job_id]['status'] ="Pdf indexed"
    
    jobs[job_id]['completed'] = True 


@upload_router.post("/")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(),
    user_id: str = Form(),
    db: SupabaseDB = Depends(get_db)):
    
    job_id = str(uuid4())
    filename = file.filename
    
    if file.content_type != "application/pdf":
            return {"data": "Only PDF files are supported"}
            
        
    contents = await file.read()
   
    storage_path = db.upload_pdf(user_id, filename =filename, file_bytes = contents)
    doc_id = db.insert_record(user_id, filename, storage_path)
    
    # UPLOAD_DIR.mkdir(exist_ok=True)
    # path = UPLOAD_DIR / file.filename

    # with open(path, "wb") as f:
    #         f.write(contents)
            
    jobs[job_id] = {
        "status": "Uploaded"
        }
    
    url = db.get_pdf_url(storage_path)
    background_tasks.add_task(
        process_pdf, 
        url, 
        job_id,
        db,
        doc_id,
        user_id
    )
    await to_thread(db.update_document_status,doc_id, "Processing")
    return {
        "status": "Processing PDF",
        "job_id" : job_id
    }

        
@upload_router.get("/progress/{job_id}")
async def file_progress(job_id: str ):
    
    async def event_generator():
            await sleep(3)

            last_status = None

            while True:

                if job_id not in jobs:
                    break

                current_status = jobs[job_id]["status"]

                if current_status != last_status:

                    yield {
                        "event": "progress",
                        "data": json.dumps({
                            "status": current_status
                        })
                    }

                    last_status = current_status

                if jobs[job_id].get("completed"):
                    yield {
                        "event": "complete",
                        "data": json.dumps({
                            "status": "Done"
                        })
                    }
                    break

                await sleep(0.5)

    return EventSourceResponse(event_generator())
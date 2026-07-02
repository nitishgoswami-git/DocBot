from asyncio import to_thread
import json
from fastapi import APIRouter
from pydantic import BaseModel
from sse_starlette import EventSourceResponse
from rag_redis.redisDB import RedisDB
from rag_redis.groq_client import GroqClient
from rag_redis.chromaDB import ChromaDB
from services.supabase_service import SupabaseDB



class ChatRequest(BaseModel):
    query: str
    USERID: str = "user"
    SESSIONID: str = "xxx"


redisDB = RedisDB()
groqclient = GroqClient()
emb = ChromaDB("rag-collection")

chat_router = APIRouter(
     prefix="/chat",
    tags=["chat"]
)

@chat_router.post('/')
async def userquery(request: ChatRequest):    
    db = SupabaseDB()
    plan = await to_thread(db.get_user_plan, request.USERID)
    
    if plan != "pro":
        if redisDB.check_rate_limit(request.USERID):
            return {"error": "Daily limit exceeded"}
    
    
    redisDB.add_message(request.USERID,request.SESSIONID,{'role' : 'user', 'content':request.query})
    
    context = emb.query_search(request.query,userid=str(request.USERID)) 
    context = context['documents'][0][0]  
    history = redisDB.get_history(request.USERID,request.SESSIONID) or []
    async def event_generator():
        full_response = ""   
        async for token in  groqclient.chat(history, context, request.query):
            full_response+=token
            yield {
                        "event": "token",
                        "data": json.dumps({
                            "chunk": token
                        })
                    }
        redisDB.add_message(request.USERID, request.SESSIONID, {'role' : 'assistant', 'content' : full_response})
        yield { 
              "event": "complete",
                        "data": json.dumps({
                            "status": "Done"
                        })}
    return EventSourceResponse(event_generator())     
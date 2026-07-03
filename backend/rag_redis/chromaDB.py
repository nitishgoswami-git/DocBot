import chromadb
import logging
import os

logger = logging.getLogger(__name__)

chroma_client = chromadb.CloudClient(
  api_key= os.environ.get("CHROMA_API_KEY"),
  tenant= os.environ.get("CHROMA_TENANT"),
  database= os.environ.get("CHROMA_DATABASE")
)

class ChromaDB:
    def __init__(self, name : str = "my_collection"):
        self.collection = chroma_client.get_or_create_collection(name=name)        
    
    def embedding(self, docs : list, userid : int):
        
        self.collection.add(
            ids=[f'{userid}-{i}' for i in range(len(docs))],
            documents=[doc["content"] for doc in docs],
            metadatas=[{"page": doc["page"], "chunk_id": doc["chunk_id"], "user_id": str(userid)} for doc in docs]        
            )
        return 'successful'
            
    def query_search(self, query: str, userid: str):
        result = self.collection.query(
            query_texts=[query],
            n_results=1,
            where={"user_id": str(userid)}  # ✅ dict, not a set
        )
        return result
        
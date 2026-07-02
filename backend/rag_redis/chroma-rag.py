from chromaDB import ChromaDB
from pprint import pprint
from redisDB import RedisDB
import uuid
from groq_client import GroqClient
from pdfParser.parser import PDFParser
from chuncker.main import Chuncker

emb = ChromaDB("rag-collection")
db = RedisDB()
groqclient = GroqClient()

USERID = uuid.uuid4()
SESSIONID = f's-{uuid.uuid4()}'

path = str(input("enter doc path you wnat to use: "))
if path :
        parser = PDFParser(path)
        print("Processing File...")
        cleaned_file = parser.cleanup()
        print('DONE !') 
        print('='*10)  
        print('Chunking Your file...')
        print('DONE !') 
        chuncker = Chuncker(cleaned_file)
        chuncks = chuncker.chunk_pages()
        print('='*10)
        print('Indexing Your doc...')
        print('DONE !') 
        emb.embedding(chuncks, userid=str(USERID))  
        print('='*10)
        
while True:
    query = str(input("You : "))
    if query.lower().strip() == "exit":
        exit()
            
    if db.check_rate_limit(USERID):
        print("you have hit the limit for today")
        break
    db.add_message(USERID,SESSIONID,{'role' : 'user', 'content':query})
    
    context = emb.query_search(query, userid=str(USERID)) 
    context = context['documents'][0][0]  
    history = db.get_history(USERID,SESSIONID) or []
    chat = groqclient.chat(history, context, query)
    print(chat)
    db.add_message(USERID, SESSIONID, {'role' : 'assistant', 'content' : chat})
from dotenv import load_dotenv
load_dotenv()

from groq import Groq, AsyncGroq
import os
import logging

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self):
        key = os.environ.get("GROQ_KEY")
        self.groqClient = AsyncGroq(api_key = key)
    
    async def chat(self, history, context, query):
      
        stream = await self.groqClient.chat.completions.create(
           messages = [
                {"role": "system", "content": f"You are a helpful assistant. Use this context: {context} also send back under a context section"},
                *history,
                {"role": "user", "content": query}
            ],model = "llama-3.3-70b-versatile", stream=True
        )
        
        async for chunk in stream:
             content = chunk.choices[0].delta.content

             if content:
                 yield content
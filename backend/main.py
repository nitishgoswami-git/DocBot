from fastapi import FastAPI
from routers.chat import chat_router
from routers.upload import upload_router
from routers.health import health_router
from routers.payment import payment_router
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()


origins = [
    os.environ.get("ORIGIN_URL"),
]
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://doc-bot-.*-nitish-s-projects-d51cbfd4\.vercel\.app|https://doc-bot-rho\.vercel\.app",
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

###Register Routes


app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(health_router)
app.include_router(payment_router)


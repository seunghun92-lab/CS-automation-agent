import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from orchestrator import create_orchestrator
from rag import create_vectorstore

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# chroma_db 없으면 자동 생성
CHROMA_PATH = os.path.join(BASE_DIR, "data", "chroma_db")
if not os.path.exists(CHROMA_PATH):
    print("chroma_db 없음 → 자동 생성 중...")
    create_vectorstore()
    print("chroma_db 생성 완료!")

orchestrator = create_orchestrator()

class ChatRequest(BaseModel):
    user_input: str

@app.post("/chat")
async def chat(request: ChatRequest):
    result = orchestrator.invoke({
        "user_input": request.user_input,
        "category": "",
        "search_results": [],
        "answer": "",
        "escalate": False,
        "retry": False,
        "retry_count": 0
    })
    return {"answer": result["answer"]}

@app.get("/health")
async def health():
    return {"status": "ok"}
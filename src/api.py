import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from orchestrator import create_orchestrator

app = FastAPI()

# CORS 설정 (React에서 요청 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "escalate": False
    })
    return {"answer": result["answer"]}

@app.get("/health")
async def health():
    return {"status": "ok"}
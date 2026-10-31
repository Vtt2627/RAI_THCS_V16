from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from agent_logic import get_learning_path, get_ai_chat_response

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StudyRequest(BaseModel):
    studentCode: str
    needAttention: List[str]

class ChatRequest(BaseModel):
    studentCode: str
    message: str

@app.post("/api/get-learning-content")
async def get_content(req: StudyRequest):
    result = get_learning_path(req.needAttention)
    return result

@app.post("/api/chat")
async def chat_with_agent(req: ChatRequest):
    reply = get_ai_chat_response(req.message)
    return {"reply": reply}

# Dòng này giúp server hiển thị giao diện index.html ở trang chủ
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
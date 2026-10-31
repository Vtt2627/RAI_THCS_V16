import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

# Import các hàm logic từ agent_logic.py
from agent_logic import get_learning_path, get_ai_chat_response

app = FastAPI()

# Gắn các thư mục static (nếu trang web của bạn để file html/js ở thư mục gốc hoặc public)
app.mount("/static", StaticFiles(directory="."), name="static")

class LearningRequest(BaseModel):
    studentCode: str  # Nhận linh hoạt bất kỳ mã nào từ client truyền lên
    need_attention: Optional[List[str]] = []

class ChatRequest(BaseModel):
    studentCode: str  # Linh hoạt cho mọi học sinh
    message: str

@app.get("/")
def read_index():
    """Trỏ về trang chủ giao diện học tập (learning.html hoặc index.html)"""
    if os.path.exists("learning.html"):
        return FileResponse("learning.html")
    return {"message": "FastAPI Server đang hoạt động!"}

@app.post("/api/get-learning-content")
def api_get_learning_content(data: LearningRequest):
    """
    Endpoint nhận danh sách cần chú ý (need_attention), 
    gọi agent_logic để phân tích và trả về lộ trình học tập tương ứng.
    """
    try:
        result = get_learning_path(data.need_attention)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
def api_chat(data: ChatRequest):
    """
    Endpoint nhận câu hỏi từ khung chat của người dùng 
    và gọi Gemini API thông qua agent_logic để trả lời.
    """
    try:
        reply = get_ai_chat_response(data.message)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
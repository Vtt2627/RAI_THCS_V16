import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional

# Import các hàm logic từ agent_logic.py
from agent_logic import get_learning_path, get_ai_chat_response

app = FastAPI()

# Định nghĩa cấu trúc dữ liệu đầu vào: Mặc định là None để biết học sinh chưa làm bài đánh giá
class LearningRequest(BaseModel):
    studentCode: Optional[str] = "HS_001"
    need_attention: Optional[List[str]] = None

class ChatRequest(BaseModel):
    studentCode: Optional[str] = "HS_001"
    message: str

@app.post("/api/get-learning-content")
def api_get_learning_content(data: LearningRequest):
    """Xử lý logic phân tích bài làm thực tế của học sinh."""
    try:
        result = get_learning_path(data.need_attention)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
def api_chat(data: ChatRequest):
    """Xử lý hỏi đáp trực tiếp với trợ lý Agent qua Gemini API."""
    try:
        reply = get_ai_chat_response(data.message)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
@app.get("/index.html")
@app.get("/learning.html")
def serve_frontend():
    """Phục vụ file giao diện chính xác."""
    if os.path.exists("learning.html"):
        return FileResponse("learning.html")
    elif os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "Server đang hoạt động nhưng không tìm thấy file giao diện."}

app.mount("/", StaticFiles(directory=".", html=True), name="static")
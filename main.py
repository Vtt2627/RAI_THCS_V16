import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional

# Import các hàm logic từ agent_logic.py
from agent_logic import get_learning_path, get_ai_chat_response

app = FastAPI()

# Định nghĩa cấu trúc dữ liệu đầu vào cho API lộ trình học tập
class LearningRequest(BaseModel):
    studentCode: Optional[str] = "HS_001"
    need_attention: Optional[List[str]] = []

# Định nghĩa cấu trúc dữ liệu đầu vào cho API chat với AI
class ChatRequest(BaseModel):
    studentCode: Optional[str] = "HS_001"
    message: str

# 1. CÁC API ENDPOINTS (Phải khai báo trước tiên để được ưu tiên xử lý tuyệt đối)
@app.post("/api/get-learning-content")
def api_get_learning_content(data: LearningRequest):
    """Xử lý phân tích 1-1 từ need_attention trả về lộ trình bù đắp hoặc nâng cao."""
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

# 2. ĐỊNH TUYẾN GIAO DIỆN (Hỗ trợ toàn diện mọi đường dẫn gốc, index.html, learning.html)
@app.get("/")
@app.get("/index.html")
@app.get("/learning.html")
def serve_frontend():
    """Tự động trả về file giao diện chính xác, ngăn chặn tuyệt đối lỗi Not Found."""
    if os.path.exists("learning.html"):
        return FileResponse("learning.html")
    elif os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "Server đang hoạt động nhưng không tìm thấy file giao diện (learning.html/index.html)."}

# 3. MOUNT STATIC FILES Ở GỐC (Phục vụ toàn bộ CSS, JS, hình ảnh, dữ liệu JSON cho giao diện)
# Đặt ở cuối cùng để các API và route trang chủ ở trên luôn được ưu tiên tuyệt đối.
app.mount("/", StaticFiles(directory=".", html=True), name="static")
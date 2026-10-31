from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

# Import các hàm xử lý logic từ tệp agent_logic.py
from agent_logic import get_learning_path, get_ai_chat_response

app = FastAPI(title="AI Responsible Learning System")

# Cấu hình CORS cho phép mọi nguồn truy cập để tránh lỗi chặn kết nối
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_index():
    """Phục vụ trang chủ đánh giá (index.html)"""
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "AI Responsible Backend đang chạy, nhưng chưa tìm thấy tệp index.html."}

@app.get("/index.html")
async def read_index_file():
    """Định tuyến dự phòng cho index.html"""
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"error": "Không tìm thấy tệp index.html"}

@app.get("/learning.html")
async def read_learning():
    """Phục vụ trang lộ trình học tập cá nhân hóa (learning.html)"""
    if os.path.exists("learning.html"):
        return FileResponse("learning.html")
    return {"error": "Không tìm thấy tệp learning.html"}

@app.post("/api/get-learning-content")
async def api_get_learning_content(request: Request):
    """
    Endpoint nhận danh sách câu sai từ client và trả về lộ trình học tập 1-1.
    Tự động bắt mọi biến truyền lên (need_attention hoặc needAttention) để chống lỗi rỗng.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    student_code = body.get("studentCode") or body.get("student_code") or "HS_DEFAULT"
    
    # Hứng trọn cả hai trường hợp tên biến mà frontend có thể gửi lên
    need_attention = body.get("need_attention") or body.get("needAttention") or []

    print(f"[LOG API] Mã học sinh: {student_code} | Các nội dung cần chú ý/sai: {need_attention}")

    # Gọi hàm xử lý phân tích lộ trình từ agent_logic.py
    result = get_learning_path(need_attention)
    return JSONResponse(content=result)

@app.post("/api/chat")
async def api_chat(request: Request):
    """
    Endpoint xử lý hỏi đáp trực tiếp với trợ lý AI.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    message = body.get("message", "").strip()
    if not message:
        return JSONResponse(content={"reply": "Vui lòng nhập nội dung câu hỏi."}, status_code=400)

    # Gọi hàm AI chat từ agent_logic.py
    reply = get_ai_chat_response(message)
    return JSONResponse(content={"reply": reply})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

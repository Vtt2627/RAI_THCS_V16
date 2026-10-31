import json
import os
import google.generativeai as genai

# Cấu hình Gemini API từ biến môi trường trên Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def load_json_file(filename):
    """Hàm đọc an toàn các tệp JSON dữ liệu."""
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Lỗi khi đọc tệp {filename}: {e}")
    return {}

def get_learning_path(need_attention):
    """
    Đồng bộ logic trả về dữ liệu cho cả 2 trường hợp:
    - Trường hợp 1: Không có lỗi -> Trả về toàn bộ khoá học nâng cao.
    - Trường hợp 2: Có lỗi -> Lọc và trả về danh sách các bài học bù đắp.
    """
    advanced_data = load_json_file("data_advanced.json")
    
    # Trường hợp 1: Học sinh đạt hết -> Trả về lộ trình nâng cao
    if not need_attention or len(need_attention) == 0:
        return {
            "message": "Bạn đã hoàn thành xuất sắc toàn bộ bài đánh giá! Dưới đây là lộ trình nâng cao:",
            "content": advanced_data
        }
    
    # Trường hợp 2: Học sinh chưa đạt -> Lọc các bài học bù đắp từ data_remedial.json
    remedial_data = load_json_file("data_remedial.json")
    
    filtered_content = {}
    for key in need_attention:
        if key in remedial_data:
            filtered_content[key] = remedial_data[key]
            
    # Nếu không khớp key nào, dự phòng trả về toàn bộ remedial hoặc advanced
    if not filtered_content:
        filtered_content = remedial_data if remedial_data else advanced_data

    return {
        "message": "Agent đã phân tích các biểu hiện chưa đạt. Dưới đây là lộ trình bù đắp kiến thức bắt buộc:",
        "content": filtered_content
    }

def get_ai_chat_response(message):
    """Xử lý hỏi đáp trực tiếp với trợ lý AI qua Gemini API."""
    if not GEMINI_API_KEY:
        return "Xin lỗi, hệ thống chưa được cấu hình khóa GEMINI_API_KEY trên server."
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(message)
        return response.text
    except Exception as e:
        return f"Xin lỗi, hiện tại tôi không thể kết nối tới mô hình AI. Chi tiết lỗi: {str(e)}"
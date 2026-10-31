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
    Phân tách rõ ràng tuyệt đối giữa lộ trình nâng cao và lộ trình bù đắp:
    - Nếu không có lỗi (need_attention trống): Trả về data_advanced.json.
    - Nếu có lỗi: Bắt buộc lấy đúng từ data_remedial.json, không lấy nhầm dữ liệu nâng cao.
    """
    advanced_data = load_json_file("data_advanced.json")
    remedial_data = load_json_file("data_remedial.json")
    
    # Trường hợp 1: Học sinh đạt hết -> Trả về lộ trình nâng cao
    if not need_attention or len(need_attention) == 0:
        return {
            "message": "Bạn đã hoàn thành xuất sắc toàn bộ bài đánh giá! Dưới đây là lộ trình nâng cao:",
            "content": advanced_data
        }
    
    # Trường hợp 2: Học sinh có biểu hiện chưa đạt -> Bắt buộc lấy từ remedial_data
    filtered_content = {}
    for key in need_attention:
        if key in remedial_data:
            filtered_content[key] = remedial_data[key]
            
    # Dự phòng an toàn: Nếu key truyền vào không khớp với remedial_data, 
    # lấy toàn bộ nội dung trong remedial_data chứ TUYỆT ĐỐI KHÔNG quay về advanced_data
    if not filtered_content:
        filtered_content = remedial_data if remedial_data else {"REM_DEFAULT": {
            "title": "Kiến thức bù đắp tổng hợp",
            "video_url": "https://www.youtube.com/embed/UlXXRd3HGT0",
            "reading_content": "Nội dung hướng dẫn ôn tập lại các kiến thức cơ bản để khắc phục điểm chưa đạt.",
            "check_questions": []
        }}

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
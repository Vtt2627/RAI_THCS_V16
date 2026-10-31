import json
import os
import google.generativeai as genai

# Cấu hình Gemini API từ biến môi trường trên server Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    
def get_ai_chat_response(message):
    """Xử lý hỏi đáp trực tiếp với trợ lý AI qua Gemini API cho mọi người dùng."""
    if not GEMINI_API_KEY:
        return "Xin lỗi, hệ thống chưa được cấu hình khóa GEMINI_API_KEY trên server."
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(message)
        return response.text
    except Exception as e:
        return f"Xin lỗi, hiện tại tôi không thể kết nối tới mô hình AI. Chi tiết lỗi: {str(e)}"

def load_json_file(filename):
    """Hàm đọc an toàn các tệp JSON dữ liệu."""
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Lỗi đọc file {filename}: {e}")
    return {}

def get_learning_path(need_attention):
    """
    Phân tích nghiêm ngặt 1-1: 
    - Dựa hoàn toàn vào danh sách `need_attention` thực tế mà học sinh làm chưa đạt.
    - Tuyệt đối không chọn đại, không gán bừa. Chỉ trích xuất đúng các bài học 
      có mã khớp chính xác với từng lỗi sai thực tế của học sinh.
    """
    advanced_data = load_json_file("data_advanced.json")
    remedial_data = load_json_file("data_remedial.json")
    
    # Nếu học sinh đạt tuyệt đối (không có lỗi nào) -> Trả về lộ trình nâng cao
    if not need_attention or len(need_attention) == 0:
        return {
            "message": "Bạn đã hoàn thành xuất sắc toàn bộ bài đánh giá! Dưới đây là lộ trình nâng cao:",
            "content": advanced_data
        }
    
    # Lọc chuẩn xác: Học sinh sai mã nào, chỉ lấy đúng bài học của mã đó trong remedial_data
    filtered_content = {}
    
    for code in need_attention:
        if code in remedial_data:
            filtered_content[code] = remedial_data[code]

    # Trả về kết quả phân tích đúng các bài học tương ứng với các lỗi học sinh gặp phải
    return {
        "message": f"Agent đã phân tích và trích xuất thành công {len(filtered_content)} bài học bù đắp tương ứng với các nội dung bạn làm chưa đạt:",
        "content": filtered_content
    }
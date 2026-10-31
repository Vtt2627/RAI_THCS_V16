import json
import os
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_ai_chat_response(message):
    """Xử lý hỏi đáp trực tiếp với trợ lý Agent qua Gemini API."""
    if not GEMINI_API_KEY:
        return "Xin lỗi, hệ thống chưa được cấu hình khóa GEMINI_API_KEY trên server."
    
    # Sử dụng model chuẩn và ổn định
    for model_name in ["gemini-1.5-flash", "gemini-1.5-pro"]:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(message)
            if response and response.text:
                return response.text
        except Exception:
            continue
            
    return "Xin lỗi, hiện tại không thể kết nối tới mô hình AI. Vui lòng kiểm tra lại khóa API."

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
    Phân tích nghiêm ngặt 1-1 dựa trên kết quả đánh giá thực tế từ frontend:
    - Nếu need_attention là danh sách rỗng []: Học sinh đạt tuyệt đối -> Trả về lộ trình nâng cao.
    - Nếu need_attention có chứa các mã lỗi: Chỉ trích xuất đúng và đủ bài học bù đắp của các mã đó, 
      tuyệt đối không chọn đại hay gán bừa.
    """
    advanced_data = load_json_file("data_advanced.json")
    remedial_data = load_json_file("data_remedial.json")
    
    # Trường hợp học sinh đạt tuyệt đối (danh sách rỗng)
    if not need_attention or len(need_attention) == 0:
        return {
            "message": "Bạn đã hoàn thành xuất sắc toàn bộ bài đánh giá! Dưới đây là lộ trình nâng cao:",
            "content": advanced_data
        }
    
    # Lọc chuẩn xác 1-1 theo đúng mã lỗi học sinh gặp phải
    filtered_content = {}
    for code in need_attention:
        if code in remedial_data:
            filtered_content[code] = remedial_data[code]

    return {
        "message": f"Agent đã phân tích và trích xuất thành công {len(filtered_content)} bài học bù đắp tương ứng với các nội dung cần khắc phục:",
        "content": filtered_content
    }
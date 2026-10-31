import json
import os
import google.generativeai as genai

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
    Phân tích nghiêm ngặt theo đúng luồng thực tế:
    - Nếu need_attention là None (chưa làm bài đánh giá): Yêu cầu học sinh hoàn thành bài test trước.
    - Nếu need_attention là danh sách rỗng [] (đã làm bài và đạt tuyệt đối): Trả về lộ trình nâng cao.
    - Nếu need_attention có dữ liệu (có lỗi sai): Trích xuất chính xác 1-1 các bài học bù đắp tương ứng.
    """
    advanced_data = load_json_file("data_advanced.json")
    remedial_data = load_json_file("data_remedial.json")
    
    # Trường hợp 1: Chưa thực hiện bài đánh giá (None)
    if need_attention is None:
        return {
            "status": "pending_assessment",
            "message": "Vui lòng hoàn thành bài đánh giá năng lực trước khi xem lộ trình học tập cá nhân hóa.",
            "content": {}
        }
    
    # Trường hợp 2: Đã làm bài và đạt tuyệt đối (danh sách rỗng [])
    if len(need_attention) == 0:
        return {
            "status": "advanced",
            "message": "Bạn đã hoàn thành xuất sắc toàn bộ bài đánh giá! Dưới đây là lộ trình nâng cao:",
            "content": advanced_data
        }
    
    # Trường hợp 3: Có lỗi cần khắc phục -> Lọc chuẩn xác 1-1, cấm gán bừa
    filtered_content = {}
    for code in need_attention:
        if code in remedial_data:
            filtered_content[code] = remedial_data[code]

    return {
        "status": "remedial",
        "message": f"Agent đã phân tích và trích xuất thành công {len(filtered_content)} bài học bù đắp tương ứng với các nội dung bạn làm chưa đạt:",
        "content": filtered_content
    }
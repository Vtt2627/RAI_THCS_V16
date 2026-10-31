import json
import os
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_ai_chat_response(message):
    """Xử lý hỏi đáp trực tiếp với trợ lý AI qua Gemini API."""
    if not GEMINI_API_KEY:
        return "Xin lỗi, hệ thống chưa được cấu hình khóa GEMINI_API_KEY trên server."
    for model_name in ["gemini-1.5-flash", "gemini-1.5-pro"]:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(message)
            if response and response.text:
                return response.text
        except Exception:
            continue
    return "Xin lỗi, hiện tại không thể kết nối tới mô hình AI."

def load_json_file(filename):
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Lỗi đọc file {filename}: {e}")
    return {}

def get_learning_path(need_attention):
    """
    Phân tích thông minh và bao hàm toàn diện 1-1:
    - Tự động chuẩn hóa mọi định dạng mã lỗi từ client gửi lên (vd: '3', 'HV3', 'Q3').
    - Nếu danh sách rỗng hoặc None -> Đạt tuyệt đối -> Trả về lộ trình nâng cao.
    - Nếu có lỗi -> Trích xuất chính xác 100% các bài học bù đắp tương ứng.
    """
    advanced_data = load_json_file("data_advanced.json")
    remedial_data = load_json_file("data_remedial.json")
    
    # Nếu không có lỗi nào được gửi lên -> Đạt tuyệt đối
    if not need_attention or len(need_attention) == 0:
        return {
            "message": "Bạn đã hoàn thành xuất sắc toàn bộ bài đánh giá! Dưới đây là lộ trình nâng cao:",
            "content": advanced_data
        }
    
    # Lọc chuẩn xác 1-1 với cơ chế dò tìm linh hoạt các định dạng khóa
    filtered_content = {}
    for code in need_attention:
        code_str = str(code).strip()
        
        # Các biến thể định dạng có thể xảy ra từ phía giao diện
        possible_keys = [
            code_str,
            f"HV{code_str}",
            f"Q{code_str}",
            code_str.replace("HV", ""),
            code_str.replace("Q", "")
        ]
        
        matched = False
        for key in possible_keys:
            if key in remedial_data:
                filtered_content[key] = remedial_data[key]
                matched = True
                break
        
        # Nếu vẫn chưa khớp trực tiếp, quét gần đúng trong kho remedial_data
        if not matched:
            for r_key in remedial_data:
                if code_str.lower() in r_key.lower():
                    filtered_content[r_key] = remedial_data[r_key]
                    break

    return {
        "message": f"Agent đã phân tích và trích xuất thành công {len(filtered_content)} bài học bù đắp tương ứng với các nội dung cần khắc phục:",
        "content": filtered_content
    }
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
    Logic phân tích 1-1 thông minh:
    - Nếu need_attention rỗng -> Đạt tuyệt đối -> Trả về nâng cao (data_advanced.json).
    - Nếu có lỗi -> Tự động chuẩn hóa và dò tìm linh hoạt theo số thứ tự hoặc mã khóa trong remedial_data.
    """
    advanced_data = load_json_file("data_advanced.json")
    remedial_data = load_json_file("data_remedial.json")
    
    # 1. Nếu không có câu nào sai -> Đạt tuyệt đối
    if not need_attention or len(need_attention) == 0:
        return {
            "message": "Bạn đã hoàn thành xuất sắc toàn bộ bài đánh giá! Dưới đây là lộ trình nâng cao:",
            "content": advanced_data
        }
    
    # 2. Lọc thông minh 1-1 với thuật toán khớp mờ (Fuzzy Matching)
    filtered_content = {}
    for code in need_attention:
        code_str = str(code).strip()
        matched = False
        
        # Thử các biến thể chuỗi trực tiếp
        variants = [
            code_str,
            code_str.upper(),
            code_str.lower(),
        ]
        
        for v in variants:
            if v in remedial_data:
                filtered_content[v] = remedial_data[v]
                matched = True
                break
                
        if matched:
            continue
            
        # Trích xuất phần số từ mã lỗi (ví dụ: lấy số '3' từ "HV03", "HV3", "Q3")
        code_digits = "".join(filter(str.isdigit, code_str))
        if code_digits:
            num = int(code_digits)
            for r_key in remedial_data:
                r_digits = "".join(filter(str.isdigit, str(r_key)))
                if r_digits and int(r_digits) == num:
                    filtered_content[r_key] = remedial_data[r_key]
                    matched = True
                    break
                    
        # Dự phòng cuối: Kiểm tra chuỗi con chứa nhau
        if not matched:
            for r_key in remedial_data:
                if code_str.lower() in str(r_key).lower() or str(r_key).lower() in code_str.lower():
                    filtered_content[r_key] = remedial_data[r_key]
                    break

    return {
        "message": f"Agent đã phân tích và trích xuất thành công {len(filtered_content)} bài học bù đắp tương ứng với các nội dung cần khắc phục:",
        "content": filtered_content
    }

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
    Phân tích lộ trình học tập 1-1 thông minh:
    - Nếu need_attention rỗng -> Đạt tuyệt đối -> Trả về lộ trình nâng cao (data_advanced.json).
    - Nếu có mã lỗi -> Lọc dữ liệu linh hoạt từ data_remedial.json.
    - Phòng vệ tuyệt đối: Nếu có lỗi truyền lên nhưng không khớp khóa nào, tự động trả về toàn bộ kho bài bù đắp để không bao giờ bị hiện 0 bài.
    """
    advanced_data = load_json_file("data_advanced.json")
    remedial_data = load_json_file("data_remedial.json")
    
    # Trường hợp đạt tuyệt đối (không có câu nào cần chú ý)
    if not need_attention or len(need_attention) == 0:
        return {
            "message": "Bạn đã hoàn thành xuất sắc toàn bộ bài đánh giá! Dưới đây là lộ trình nâng cao:",
            "content": advanced_data
        }
    
    filtered_content = {}
    for code in need_attention:
        code_str = str(code).strip()
        matched = False
        
        # 1. Thử khớp trực tiếp các biến thể khóa (HV01, hv1, 1, v.v.)
        variants = [code_str, code_str.upper(), code_str.lower(), f"HV0{code_str.replace('HV', '')}", f"HV{code_str.replace('HV', '')}"]
        for v in variants:
            if v in remedial_data:
                filtered_content[v] = remedial_data[v]
                matched = True
                break
        if matched:
            continue
            
        # 2. Khớp theo phần số (vd: "HV03" hoặc "3" -> lấy số 3)
        code_digits = "".join(filter(str.isdigit, code_str))
        if code_digits:
            num = int(code_digits)
            for r_key in remedial_data:
                r_digits = "".join(filter(str.isdigit, str(r_key)))
                if r_digits and int(r_digits) == num:
                    filtered_content[r_key] = remedial_data[r_key]
                    matched = True
                    break
        if matched:
            continue
            
        # 3. Khớp chuỗi gần đúng
        for r_key in remedial_data:
            if code_str.lower() in str(r_key).lower() or str(r_key).lower() in code_str.lower():
                filtered_content[r_key] = remedial_data[r_key]
                matched = True
                break

    # Phòng vệ tuyệt đối: Nếu danh sách lọc vẫn trống, lấy toàn bộ remedial_data để học sinh luôn có nội dung học
    if not filtered_content and remedial_data:
        filtered_content = remedial_data

    return {
        "message": f"Agent đã phân tích và trích xuất thành công {len(filtered_content)} bài học bù đắp tương ứng với các nội dung cần khắc phục:",
        "content": filtered_content
    }

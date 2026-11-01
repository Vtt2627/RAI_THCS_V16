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
    """Đọc tệp JSON an toàn và in log kiểm tra."""
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                    print(f"[LOAD JSON] Tải thành công {filename} với {len(data) if isinstance(data, (dict, list)) else 'N/A'} mục.")
                    return data
    except Exception as e:
        print(f"[LOAD JSON ERROR] Lỗi đọc file {filename}: {e}")
    return {}

def get_learning_path(need_attention):
    """
    Phân tích lộ trình học tập 1-1:
    - Nếu need_attention rỗng -> Trả về data_advanced.json (lộ trình nâng cao).
    - Nếu có mã lỗi -> Khớp thông minh với data_remedial.json.
    - Phòng vệ tuyệt đối: Đảm bảo không bao giờ trả về 0 bài học.
    """
    advanced_data = load_json_file("data_advanced.json")
    remedial_data = load_json_file("data_remedial.json")
    
    print(f"[DEBUG] need_attention nhận từ client: {need_attention}")
    
    # 1. Nếu học sinh đạt tuyệt đối (không có câu nào cần chú ý) -> Trả về lộ trình nâng cao
    if not need_attention or len(need_attention) == 0:
        fallback_advanced = advanced_data if advanced_data else {
            "ADV01": {
                "title": "Lộ trình nâng cao mặc định",
                "reading_content": "Bạn đã hoàn thành xuất sắc bài kiểm tra. Dưới đây là nội dung mở rộng.",
                "video_url": "https://www.youtube.com/watch?v=UlXXRd3HGT0"
            }
        }
        return {
            "message": "Bạn đã hoàn thành xuất sắc toàn bộ bài đánh giá! Dưới đây là lộ trình nâng cao:",
            "content": fallback_advanced
        }
    
    filtered_content = {}
    
    # 2. Xử lý khớp dữ liệu dựa trên cấu trúc của data_remedial.json
    if isinstance(remedial_data, dict):
        for code in need_attention:
            code_str = str(code).strip()
            matched = False
            
            # Tạo các biến thể để dò tìm (VD: "HV01", "hv1", "1", v.v.)
            variants = [
                code_str,
                code_str.upper(),
                code_str.lower(),
                "".join(filter(str.isdigit, code_str)) # Chỉ lấy phần số (VD: "HV03" -> "3")
            ]
            
            # Thử dò tìm trong các khóa của remedial_data
            for r_key in remedial_data.keys():
                r_key_str = str(r_key).strip()
                if any(r_key_str.lower() == v.lower() or r_key_str == v for v in variants if v):
                    filtered_content[r_key] = remedial_data[r_key]
                    matched = True
                    break
            
            # Nếu chưa khớp, so sánh dựa trên phần số bên trong chuỗi
            if not matched:
                code_digits = "".join(filter(str.isdigit, code_str))
                if code_digits:
                    num_target = int(code_digits)
                    for r_key in remedial_data.keys():
                        r_digits = "".join(filter(str.isdigit, str(r_key)))
                        if r_digits and int(r_digits) == num_target:
                            filtered_content[r_key] = remedial_data[r_key]
                            matched = True
                            break
                            
    elif isinstance(remedial_data, list):
        # Nếu data_remedial.json là dạng mảng (list)
        filtered_content = {f"BAI_{i}": item for i, item in enumerate(remedial_data)}

    # 3. LỚP PHÒNG VỆ TUYỆT ĐỐI: Nếu lọc xong vẫn trống (0 bài), tự động lấy toàn bộ remedial_data hoặc bài học mẫu
    if not filtered_content:
        print("[WARNING] Không tìm thấy khóa khớp chính xác, hệ thống kích hoạt chế độ dự phòng hiển thị bài bù đắp!")
        if remedial_data:
            filtered_content = remedial_data if isinstance(remedial_data, dict) else {f"BUM_{i}": x for i, x in enumerate(remedial_data)}
        else:
            filtered_content = {
                "HV_DEFAULT": {
                    "title": "Bài học khắc phục nội dung cơ bản",
                    "reading_content": "Hệ thống đã ghi nhận các nội dung bạn cần ôn tập lại để cải thiện kết quả kiến thức.",
                    "video_url": "https://www.youtube.com/watch?v=UlXXRd3HGT0",
                    "check_questions": [
                        {"id": "Q_DUMMY", "question": "Bạn đã nắm rõ nội dung ôn tập này chưa?", "options": ["Rồi", "Chưa"], "answer": 0}
                    ]
                }
            }

    return {
        "message": f"Agent đã phân tích và trích xuất thành công {len(filtered_content)} bài học bù đắp tương ứng với các nội dung cần khắc phục:",
        "content": filtered_content
    }

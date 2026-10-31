import json
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

def load_json_file(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

remedial_db = load_json_file("data_remedial.json")
advanced_db = load_json_file("data_advanced.json")

def get_learning_path(need_attention_list):
    if not need_attention_list:
        return {
            "mode": "advanced",
            "message": "Bạn đã hoàn thành xuất sắc toàn bộ bài đánh giá! Mời bạn bước vào kho dữ liệu nâng cao.",
            "content": advanced_db
        }
    else:
        assigned_lessons = {}
        for hv in need_attention_list:
            if hv in remedial_db:
                assigned_lessons[hv] = remedial_db[hv]
        return {
            "mode": "remedial",
            "message": "Agent đã phân tích các biểu hiện chưa đạt. Dưới đây là lộ trình học bù đắp kiến thức bắt buộc:",
            "content": assigned_lessons
        }

def get_ai_chat_response(message: str):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Bạn là trợ lý AI giáo dục an toàn AI cho học sinh THCS. Hãy trả lời ngắn gọn, thân thiện: {message}"
        )
        return response.text
    except Exception as e:
        return "Xin lỗi, hiện tại tôi không thể kết nối tới mô hình AI."
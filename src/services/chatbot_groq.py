"""
Groq Chatbot - Thay thế Rasa/KB bằng API đơn giản
"""

import os
from typing import Optional
from dotenv import load_dotenv
from groq import Groq
from .weather_service import WeatherService

# Load environment variables
load_dotenv()

class GroqChatbot:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.1-8b-instant"  # Model mới nhất
        self.weather_service = WeatherService()
        
        # Context về tòa nhà để chatbot hiểu
        self.system_prompt = """
Bạn là trợ lý thông minh tại tòa nhà 8 tầng số 03 Quang Trung, Đà Nẵng.

Thông tin tòa nhà:
- Tầng 1: Lễ tân, sảnh chờ, khu tiếp khách, pantry/cà phê mini
- Tầng 2: Phòng họp lớn 12–16 người, 2 phòng họp nhỏ 4–6 người
- Tầng 3: Khu làm việc chính, 1 phòng họp nhỏ, khu phone booth
- Tầng 4: Phòng training/sự kiện 30–40 người, sân thượng nhỏ
- Thang máy: gần khu lễ tân tầng 1
- Bãi xe: phía sau tòa nhà, vào cổng hông
- Wifi khách: GUEST-03QT (mật khẩu hỏi lễ tân)
- Giờ làm việc: 08:00–17:30 (lễ tân), 07:30–21:00 (tòa nhà)
- Thời gian xây dựng: xây dựng đầu năm 2008 và đưa vào sử dụng từ tháng 3 năm 2009

Địa điểm vui chơi gần đây:
- Sông Hàn: cách 300–500m, đi bộ 5–7 phút
- Cầu Rồng: cách 1.8km, xe máy 7–10 phút
- Chợ Hàn: cách ~1km, đặc sản Đà Nẵng
- Biển Mỹ Khê: cách ~3.5–4km, 10–15 phút
- Phố cà phê Nguyễn Văn Linh: cách ~1km

Trả lời ngắn gọn, thân thiện bằng tiếng Việt. Nếu không biết, hãy nói "Tôi chưa có thông tin về điều này, bạn có thể hỏi lễ tân tầng 1."
"""

    def chat(self, user_message: str) -> str:
        """Gửi tin nhắn và nhận phản hồi từ Groq"""
        if not self.client:
            return "Chưa cấu hình API key. Vui lòng thêm GROQ_API_KEY vào environment variables."
        
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        weather_info = self.weather_service.get_tomorrow_forecast()
        if weather_info:
            weather_context = weather_info["text"]
            activities = "\n".join(f"- {act}" for act in weather_info["activities"])
            messages.append({
                "role": "system",
                "content": (
                    f"Cập nhật thời tiết tự động cho Đà Nẵng:\n{weather_context}\n\n"
                    f"Gợi ý hoạt động phù hợp:\n{activities}"
                )
            })
        elif self.weather_service.last_error:
            messages.append({
                "role": "system",
                "content": (
                    "Hiện chưa lấy được dữ liệu thời tiết từ OpenWeatherMap. "
                    f"Lý do kỹ thuật: {self.weather_service.last_error}. "
                    "Nếu người dùng hỏi thời tiết, hãy xin lỗi và hướng dẫn họ hỏi lễ tân."
                )
            })

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages + [
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Lỗi: {str(e)}"
    
    def is_available(self) -> bool:
        """Kiểm tra API có khả dụng không"""
        return self.api_key is not None

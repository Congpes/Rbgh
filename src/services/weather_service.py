import os
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import requests


class WeatherService:
    """Wrapper gọi OpenWeatherMap để lấy dự báo thời tiết Đà Nẵng"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (
            api_key
            or os.getenv("OPENWEATHER_API_KEY")
            or os.getenv("WEATHER_API_KEY")
            or os.getenv("WEATHERAPI_KEY")
        )
        self.base_url = "https://api.openweathermap.org/data/2.5/forecast"
        self.city_query = "Da Nang,vn"
        self.last_error: Optional[str] = None

    def _get_timezone(self, data: Dict) -> timezone:
        offset = data.get("city", {}).get("timezone", 0)
        return timezone(timedelta(seconds=offset))

    def get_tomorrow_forecast(self) -> Optional[Dict]:
        if not self.api_key:
            self.last_error = "Thiếu OPENWEATHER_API_KEY/WEATHER_API_KEY"
            return None
        try:
            resp = requests.get(
                self.base_url,
                params={
                    "q": self.city_query,
                    "units": "metric",
                    "appid": self.api_key,
                    "lang": "vi",
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            self.last_error = f"Lỗi gọi OpenWeather: {exc}"
            return None

        tz = self._get_timezone(data)
        now_local = datetime.now(tz)
        tomorrow_date = (now_local + timedelta(days=1)).date()

        slots = []
        for item in data.get("list", []):
            dt = datetime.utcfromtimestamp(item["dt"]).replace(tzinfo=timezone.utc).astimezone(tz)
            if dt.date() == tomorrow_date:
                slots.append((dt, item))

        if not slots:
            self.last_error = "API chưa có dữ liệu dự báo cho ngày mai"
            return None

        temps = [slot[1]["main"]["temp"] for slot in slots]
        humidity = [slot[1]["main"].get("humidity", 0) for slot in slots]
        pops = [slot[1].get("pop", 0) for slot in slots]
        descriptions = [
            slot[1]["weather"][0].get("description", "").lower()
            for slot in slots
            if slot[1].get("weather")
        ]

        cond = Counter(descriptions).most_common(1)[0][0] if descriptions else "không rõ"
        rain_prob = round(sum(pops) / len(pops) * 100, 1)

        summary = {
            "date": tomorrow_date.strftime("%d/%m/%Y"),
            "min_temp": round(min(temps), 1),
            "max_temp": round(max(temps), 1),
            "avg_humidity": round(sum(humidity) / len(humidity), 0),
            "condition": cond,
            "rain_probability": rain_prob,
            "slots": slots,
        }

        summary["activities"] = self._suggest_activities(summary)
        summary["text"] = self._format_summary(summary)
        self.last_error = None
        return summary

    def _format_summary(self, info: Dict) -> str:
        return (
            f"Dự báo ngày mai ({info['date']}) tại Đà Nẵng: trời {info['condition']}, "
            f"nhiệt độ từ {info['min_temp']}°C đến {info['max_temp']}°C, "
            f"độ ẩm trung bình {info['avg_humidity']}%, "
            f"xác suất mưa khoảng {info['rain_probability']}%."
        )

    def _suggest_activities(self, info: Dict) -> list:
        cond = info["condition"].lower()
        rain = info["rain_probability"]
        max_temp = info["max_temp"]
        activities = []

        if rain >= 50 or "mưa" in cond:
            activities = [
                "Khám phá bảo tàng Điêu khắc Chăm hoặc bảo tàng Mỹ thuật Đà Nẵng.",
                "Thưởng thức cà phê, đọc sách ở các quán rooftop view sông Hàn.",
                "Trải nghiệm spa hoặc các khu giải trí trong nhà như VR/zoo mini.",
            ]
        elif max_temp >= 34:
            activities = [
                "Đi biển buổi sáng sớm hoặc chiều muộn để tránh nắng gắt.",
                "Tham quan Sun World Danang Wonders, chọn khung giờ mát.",
                "Thưởng thức hải sản tối muộn ven biển Nguyễn Tất Thành.",
            ]
        else:
            activities = [
                "Dạo bộ bên bờ sông Hàn và check-in cầu Rồng, cầu Tình Yêu.",
                "Chạy bộ/đạp xe quanh cầu Thuận Phước hoặc bán đảo Sơn Trà.",
                "Lên Bà Nà Hills hoặc núi Sơn Trà cho chuyến picnic nhẹ.",
            ]

        return activities


from typing import Any, Text, Dict, List
from datetime import datetime
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.services.kb_chromadb import ChromaKB


class ActionGetTime(Action):
    def name(self) -> Text:
        return "action_get_time"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        now = datetime.now().strftime("%H:%M")
        dispatcher.utter_message(text=f"Bây giờ là {now}.")
        return []


class ActionGetDate(Action):
    def name(self) -> Text:
        return "action_get_date"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        today = datetime.now().strftime("%d/%m/%Y")
        weekday = ["Thứ Hai","Thứ Ba","Thứ Tư","Thứ Năm","Thứ Sáu","Thứ Bảy","Chủ Nhật"][datetime.now().weekday()]
        dispatcher.utter_message(text=f"Hôm nay là {weekday}, ngày {today}.")
        return []


class ActionGetWeather(Action):
    def name(self) -> Text:
        return "action_get_weather"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {"latitude": 16.0678, "longitude": 108.2208, "current_weather": True}
            r = requests.get(url, params=params, timeout=4)
            cw = r.json().get("current_weather", {})
            temp = cw.get("temperature")
            wind = cw.get("windspeed")
            if temp is not None:
                dispatcher.utter_message(text=f"Nhiệt độ hiện tại ở Đà Nẵng khoảng {temp}°C, gió {wind} km/h.")
            else:
                dispatcher.utter_message(text="Tôi chưa lấy được thời tiết ngay lúc này, bạn có thể thử lại sau.")
        except Exception:
            dispatcher.utter_message(text="Tôi chưa lấy được thời tiết ngay lúc này, bạn có thể thử lại sau.")
        return []


class ActionKbLookup(Action):
    def name(self) -> Text:
        return "action_kb_lookup"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        text = tracker.latest_message.get("text") or ""
        kb = ChromaKB()
        hits = kb.query(text, top_k=1, min_score=0.2)
        if hits:
            dispatcher.utter_message(text=hits[0].get("text", ""))
        else:
            dispatcher.utter_message(text="Xin lỗi, tôi chưa có câu trả lời phù hợp.")
        return []



from typing import List, Dict, Any
import requests


class RasaClient:
    def __init__(self, base_url: str = "http://localhost:5005") -> None:
        self.base_url = base_url.rstrip("/")

    def send_message(self, sender: str, text: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/webhooks/rest/webhook"
        payload = {"sender": sender, "message": text}
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # Rasa trả mảng events/messages; ta chỉ trả nguyên dạng
        return data



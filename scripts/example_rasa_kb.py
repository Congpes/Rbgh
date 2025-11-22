import os
import sys
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.services.kb_chromadb import ChromaKB
from src.services.rasa_client import RasaClient


def is_rasa_up(url: str = "http://localhost:5005") -> bool:
    try:
        requests.get(url, timeout=2)
        return True
    except Exception:
        return False


def main():
    user_text = "Hướng dẫn nhận đồ"
    rasa = RasaClient()
    kb = ChromaKB()

    if is_rasa_up():
        try:
            resp = rasa.send_message(sender="tester", text=user_text)
            print("Rasa response:", resp)
        except Exception as e:
            print("Rasa lỗi:", e)
    else:
        print("Rasa chưa chạy. Thử truy vấn KB thay thế...")
        results = kb.query(user_text, top_k=3)
        for r in results:
            print("KB hit:", r["id"], "-", r["text"]) 


if __name__ == "__main__":
    main()



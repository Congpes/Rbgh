"""
Lưu/khôi phục phiên giao hàng để robot có thể đọc và thực thi.
"""

import json
import os
from typing import Any, Dict


def default_session_path() -> str:
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'data')
    base = os.path.normpath(base)
    if not os.path.isdir(base):
        os.makedirs(base, exist_ok=True)
    return os.path.join(base, 'session.json')


def save_session(path: str, data: Dict[str, Any]) -> None:
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Lỗi lưu session: {e}")


def load_session(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Lỗi đọc session: {e}")
        return {}


def clear_session(path: str) -> None:
    try:
        if os.path.isfile(path):
            os.remove(path)
    except Exception as e:
        print(f"Lỗi xóa session: {e}")


def load_rooms() -> Dict[str, Any]:
    """Load dữ liệu phòng từ file rooms.json"""
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'data')
    base = os.path.normpath(base)
    rooms_path = os.path.join(base, 'rooms.json')
    
    if not os.path.isfile(rooms_path):
        return {}
    
    try:
        with open(rooms_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Lỗi đọc rooms: {e}")
        return {}



"""
Delivery Manager - Quản lý hàng đợi giao hàng
Xử lý việc sắp xếp phòng theo thứ tự giao hàng và quản lý tiến trình
"""

import json
import re
from typing import List, Dict, Any, Optional
from src.utils.storage import load_rooms

class DeliveryManager:
    """Quản lý hàng đợi giao hàng"""
    
    def __init__(self):
        self.delivery_queue: List[Dict[str, Any]] = []
        self.current_delivery_index = 0
        self.rooms_data = load_rooms()
    
    def add_delivery(self, room_id: str, cabinets: List[Dict]) -> None:
        """Thêm một phòng vào hàng đợi giao hàng"""
        room_info = self.rooms_data.get(room_id, {})
        delivery_item = {
            "room_id": room_id,
            "room_info": room_info,
            "cabinets": cabinets,
            "status": "pending"  # pending, delivering, completed
        }
        self.delivery_queue.append(delivery_item)
        self.sort_delivery_queue()
    
    def sort_delivery_queue(self) -> None:
        """Sắp xếp hàng đợi theo thứ tự: tầng tăng dần, số phòng tăng dần.
        An toàn với tên phòng không phải dạng số (ví dụ: "Sảnh chính")."""
        def sort_key(item):
            room_info = item.get("room_info", {}) or {}
            # Tầng
            try:
                floor = int(room_info.get("floor", 1))
            except Exception:
                floor = 1
            # Lấy số ở cuối tên phòng, nếu không có thì 0
            name = str(room_info.get("name", ""))
            match = re.search(r"(\d+)$", name)
            room_number = int(match.group(1)) if match else 0
            return (floor, room_number)
        
        self.delivery_queue.sort(key=sort_key)
    
    def get_current_delivery(self) -> Optional[Dict[str, Any]]:
        """Lấy phòng giao hàng hiện tại"""
        if 0 <= self.current_delivery_index < len(self.delivery_queue):
            return self.delivery_queue[self.current_delivery_index]
        return None
    
    def mark_current_delivery_completed(self) -> bool:
        """Đánh dấu phòng giao hàng hiện tại đã hoàn thành"""
        if 0 <= self.current_delivery_index < len(self.delivery_queue):
            self.delivery_queue[self.current_delivery_index]["status"] = "completed"
            return True
        return False
    
    def move_to_next_delivery(self) -> bool:
        """Chuyển sang phòng giao hàng tiếp theo"""
        self.current_delivery_index += 1
        return self.current_delivery_index < len(self.delivery_queue)
    
    def has_more_deliveries(self) -> bool:
        """Kiểm tra còn phòng nào cần giao không"""
        return self.current_delivery_index < len(self.delivery_queue)
    
    def get_delivery_progress(self) -> tuple:
        """Lấy tiến trình giao hàng (phòng hiện tại, tổng số phòng)"""
        return (self.current_delivery_index + 1, len(self.delivery_queue))
    
    def get_pending_deliveries(self) -> List[Dict[str, Any]]:
        """Lấy danh sách phòng chưa giao"""
        return [item for item in self.delivery_queue if item["status"] == "pending"]
    
    def get_completed_deliveries(self) -> List[Dict[str, Any]]:
        """Lấy danh sách phòng đã giao xong"""
        return [item for item in self.delivery_queue if item["status"] == "completed"]
    
    def clear_completed_deliveries(self) -> None:
        """Xóa các phòng đã giao xong khỏi hàng đợi"""
        self.delivery_queue = [item for item in self.delivery_queue if item["status"] != "completed"]
        # Điều chỉnh index nếu cần
        if self.current_delivery_index >= len(self.delivery_queue):
            self.current_delivery_index = max(0, len(self.delivery_queue) - 1)
    
    def reset(self) -> None:
        """Reset về trạng thái ban đầu"""
        self.delivery_queue = []
        self.current_delivery_index = 0
    
    def get_delivery_summary(self) -> Dict[str, Any]:
        """Lấy thông tin tổng quan về giao hàng"""
        current = self.get_current_delivery()
        progress = self.get_delivery_progress()
        
        return {
            "current_delivery": current,
            "progress": progress,
            "total_deliveries": len(self.delivery_queue),
            "completed_count": len(self.get_completed_deliveries()),
            "pending_count": len(self.get_pending_deliveries())
        }

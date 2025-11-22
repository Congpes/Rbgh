"""
STT Learning System - Hệ thống học từ lỗi STT
Lưu trữ và học từ các lỗi nhận dạng để cải thiện độ chính xác
"""

import json
import os
from typing import Dict, List, Tuple
from datetime import datetime

class STTLearning:
    def __init__(self, learning_file: str = "data/stt_learning.json"):
        self.learning_file = learning_file
        self.learning_data = self._load_learning_data()
    
    def _load_learning_data(self) -> Dict:
        """Tải dữ liệu học từ file"""
        if os.path.exists(self.learning_file):
            try:
                with open(self.learning_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Khởi tạo dữ liệu mới
        return {
            "corrections": {},  # {wrong_text: correct_text}
            "confidence_scores": {},  # {text: confidence}
            "learning_history": []  # [(timestamp, wrong, correct)]
        }
    
    def _save_learning_data(self):
        """Lưu dữ liệu học vào file"""
        os.makedirs(os.path.dirname(self.learning_file), exist_ok=True)
        with open(self.learning_file, "w", encoding="utf-8") as f:
            json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
    
    def report_error(self, wrong_text: str, correct_text: str):
        """Báo cáo lỗi nhận dạng"""
        wrong_clean = wrong_text.strip().lower()
        correct_clean = correct_text.strip().lower()
        
        if wrong_clean != correct_clean:
            # Lưu correction
            self.learning_data["corrections"][wrong_clean] = correct_clean
            
            # Thêm vào lịch sử
            self.learning_data["learning_history"].append({
                "timestamp": datetime.now().isoformat(),
                "wrong": wrong_clean,
                "correct": correct_clean
            })
            
            # Giới hạn lịch sử 1000 mục
            if len(self.learning_data["learning_history"]) > 1000:
                self.learning_data["learning_history"] = self.learning_data["learning_history"][-1000:]
            
            self._save_learning_data()
            return True
        return False
    
    def get_corrections(self) -> Dict[str, str]:
        """Lấy danh sách corrections đã học"""
        return self.learning_data["corrections"].copy()
    
    def apply_learned_corrections(self, text: str) -> str:
        """Áp dụng corrections đã học vào text"""
        if not text:
            return text
        
        s = text.strip().lower()
        
        # Áp dụng corrections đã học
        for wrong, correct in self.learning_data["corrections"].items():
            if wrong in s:
                s = s.replace(wrong, correct)
        
        return s
    
    def get_learning_stats(self) -> Dict:
        """Thống kê học tập"""
        total_corrections = len(self.learning_data["corrections"])
        recent_corrections = len([
            h for h in self.learning_data["learning_history"]
            if datetime.fromisoformat(h["timestamp"]).date() == datetime.now().date()
        ])
        
        return {
            "total_corrections": total_corrections,
            "recent_corrections": recent_corrections,
            "most_common_errors": self._get_most_common_errors()
        }
    
    def _get_most_common_errors(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Lấy lỗi phổ biến nhất"""
        error_counts = {}
        for history in self.learning_data["learning_history"]:
            wrong = history["wrong"]
            error_counts[wrong] = error_counts.get(wrong, 0) + 1
        
        return sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def export_learning_data(self, export_file: str = "data/stt_learning_export.json"):
        """Xuất dữ liệu học để backup"""
        with open(export_file, "w", encoding="utf-8") as f:
            json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
    
    def import_learning_data(self, import_file: str):
        """Nhập dữ liệu học từ file"""
        if os.path.exists(import_file):
            with open(import_file, "r", encoding="utf-8") as f:
                imported_data = json.load(f)
                self.learning_data.update(imported_data)
                self._save_learning_data()

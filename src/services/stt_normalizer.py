"""
STT Text Normalizer - Chuẩn hóa văn bản từ Speech-to-Text
Xử lý lỗi thường gặp khi Vosk nhận dạng tiếng Việt
"""

from .stt_learning import STTLearning

class STTNormalizer:
    def __init__(self):
        self.learning = STTLearning()
        # Mapping lỗi thường gặp từ STT
        self.replacements = {
            # Thời gian
            "hom nay": "hôm nay",
            "hom nay la": "hôm nay là", 
            "hom nay la ngay": "hôm nay là ngày",
            "hom nay la ngay bao nhieu": "hôm nay là ngày bao nhiêu",
            "hom nay la ngay may": "hôm nay là ngày mấy",
            "bay gio": "bây giờ",
            "bay gio may gio": "bây giờ mấy giờ",
            "may gio": "mấy giờ",
            "thoi gian": "thời gian",
            "ngay bao nhieu": "ngày bao nhiêu",
            "ngay may": "ngày mấy",
            
            # Thời tiết
            "thoi tiet": "thời tiết",
            "thoi tiet hom nay": "thời tiết hôm nay",
            "troi hom nay": "trời hôm nay",
            "troi hom nay the nao": "trời hôm nay thế nào",
            
            # Tòa nhà
            "toa nha": "tòa nhà",
            "dia chi toa nha": "địa chỉ tòa nhà",
            "dia chi": "địa chỉ",
            "so do tang": "sơ đồ tầng",
            "so do tang 1": "sơ đồ tầng 1",
            "thang may": "thang máy",
            "thang may o dau": "thang máy ở đâu",
            "gui xe": "gửi xe",
            "gui xe o dau": "gửi xe ở đâu",
            "gio lam viec": "giờ làm việc",
            "gio lam viec le tan": "giờ làm việc lễ tân",
            "phong hop": "phòng họp",
            
            # Hướng dẫn
            "huong dan": "hướng dẫn",
            "huong dan nhan do": "hướng dẫn nhận đồ",
            "nhan do": "nhận đồ",
            "nhan do nhu the nao": "nhận đồ như thế nào",
            
            # Vui chơi
            "gan day": "gần đây",
            "gan day co cho vui choi nao": "gần đây có chỗ vui chơi nào",
            "cho vui choi": "chỗ vui chơi",
            "quan ca phe": "quán cà phê",
            "quan ca phe nao gan day": "quán cà phê nào gần đây",
            
            # Chào hỏi
            "xin chao": "xin chào",
            "chao ban": "chào bạn",
            "chao": "chào",
            "chao buoi sang": "chào buổi sáng",
            "chao buoi toi": "chào buổi tối",
            "cam on": "cảm ơn",
            "tam biet": "tạm biệt",
            "tam biet ban": "tạm biệt bạn",
            
            # Hỗ trợ
            "lien he": "liên hệ",
            "ho tro": "hỗ trợ",
            "lien he ho tro": "liên hệ hỗ trợ",
            "can ho tro": "cần hỗ trợ",
            "giup do": "giúp đỡ",
            
            # Robot
            "robot": "robot",
            "gioi thieu robot": "giới thiệu robot",
            "robot la gi": "robot là gì",
            "robot co the lam gi": "robot có thể làm gì",
        }
    
    def normalize(self, text: str) -> str:
        """
        Chuẩn hóa văn bản từ STT
        
        Args:
            text: Văn bản thô từ STT
            
        Returns:
            Văn bản đã chuẩn hóa
        """
        if not text:
            return ""
            
        # Chuyển về lowercase và loại bỏ khoảng trắng thừa
        s = text.strip().lower()
        
        # Lọc bỏ text rác (chỉ giữ lại từ tiếng Việt có nghĩa)
        import re
        # Loại bỏ ký tự đặc biệt và số
        s = re.sub(r'[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', ' ', s)
        # Loại bỏ khoảng trắng thừa
        s = ' '.join(s.split())
        
        # Mapping lỗi cụ thể cho "chào bạn"
        if "chao" in s or "chào" in s:
            if "ban" in s or "bạn" in s:
                return "chào bạn"
            return "xin chào"
        
        # Áp dụng mapping lỗi khác
        for wrong, correct in self.replacements.items():
            s = s.replace(wrong, correct)
        
        # Áp dụng corrections đã học
        s = self.learning.apply_learned_corrections(s)
        
        return s
    
    def add_mapping(self, wrong: str, correct: str):
        """Thêm mapping lỗi mới"""
        self.replacements[wrong.lower()] = correct
    
    def get_common_phrases(self):
        """Lấy danh sách câu phổ biến để làm grammar cho Vosk"""
        return [
            "hôm nay là ngày bao nhiêu",
            "hôm nay là ngày mấy", 
            "bây giờ mấy giờ",
            "thời tiết hôm nay",
            "trời hôm nay thế nào",
            "địa chỉ tòa nhà",
            "sơ đồ tầng 1",
            "thang máy ở đâu",
            "gửi xe ở đâu",
            "giờ làm việc lễ tân",
            "phòng họp",
            "hướng dẫn nhận đồ",
            "gần đây có chỗ vui chơi nào",
            "quán cà phê nào gần đây",
            "xin chào",
            "chào bạn",
            "cảm ơn",
            "tạm biệt",
            "liên hệ hỗ trợ",
            "giới thiệu robot",
        ]
    
    def report_error(self, wrong_text: str, correct_text: str):
        """Báo cáo lỗi nhận dạng để học"""
        return self.learning.report_error(wrong_text, correct_text)
    
    def get_learning_stats(self):
        """Thống kê học tập"""
        return self.learning.get_learning_stats()

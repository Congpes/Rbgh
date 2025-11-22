"""
Component tủ đơn lẻ trong bảng trạng thái
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class CabinetTile(QWidget):
    """Tile hiển thị trạng thái một tủ"""
    
    # Signal
    cabinet_clicked = pyqtSignal(str)  # cabinet_id
    
    def __init__(self, cabinet_id, cabinet_name, parent=None):
        super().__init__(parent)
        self.cabinet_id = cabinet_id
        self.cabinet_name = cabinet_name
        self.room_number = None
        self.has_delivery = False
        self.init_ui()
        
    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Label hiển thị số phòng hoặc "No delivery"
        self.status_label = QLabel("No delivery")
        self.status_label.setFont(QFont("Arial", 28, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: white;
            background: transparent;
        """)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Style mặc định (No delivery) - có viền rõ ràng
        self.setStyleSheet("""
            QWidget {
                background-color: #6257CA;
                border-radius: 15px;
                border: 3px solid #4A4A4A;
            }
        """)
        
    def set_delivery_room(self, room_number):
        """Cập nhật tủ có đồ cho phòng"""
        self.room_number = room_number
        self.has_delivery = True
        self.status_label.setText(str(room_number))
        
        # Style cho tủ có đồ (màu xanh ngọc sáng) - có viền rõ ràng
        self.setStyleSheet("""
            QWidget {
                background-color: #31C7E9;
                border-radius: 15px;
                border: 3px solid #1E8FA8;
            }
        """)
        
    def set_no_delivery(self):
        """Cập nhật tủ không có đồ"""
        self.room_number = None
        self.has_delivery = False
        self.status_label.setText("No delivery")
        
        # Style cho tủ không có đồ (màu tím nhạt) - có viền rõ ràng
        self.setStyleSheet("""
            QWidget {
                background-color: #6257CA;
                border-radius: 15px;
                border: 3px solid #4A4A4A;
            }
        """)
        
    def mousePressEvent(self, event):
        """Xử lý click vào tủ"""
        if event.button() == Qt.LeftButton:
            self.cabinet_clicked.emit(self.cabinet_id)
        super().mousePressEvent(event)

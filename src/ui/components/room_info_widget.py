"""
Component hiển thị thông tin phòng đang được giao
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class RoomInfoWidget(QWidget):
    """Widget hiển thị thông tin phòng đang giao"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Label "Arriving room XXX" - tăng kích thước chữ
        self.room_label = QLabel("Arriving room 314")
        self.room_label.setFont(QFont("Arial", 36, QFont.Bold))
        self.room_label.setAlignment(Qt.AlignCenter)
        self.room_label.setStyleSheet("""
            color: white;
            margin: 0px;
        """)
        layout.addWidget(self.room_label)
        
        # Label hướng dẫn - tăng kích thước chữ
        self.instruction_label = QLabel("Please do not block the robot's path. Thank you.")
        self.instruction_label.setFont(QFont("Arial", 20))
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setStyleSheet("""
            color: white;
            margin: 0px;
        """)
        layout.addWidget(self.instruction_label)
        
        self.setLayout(layout)
        
    def set_room_number(self, room_number):
        """Cập nhật số phòng"""
        self.room_label.setText(f"Arriving room {room_number}")

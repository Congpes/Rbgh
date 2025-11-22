"""
Back Button Component - Button quay về với mũi tên
"""
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt, pyqtSignal

class BackButton(QPushButton):
    """Button quay về với icon mũi tên"""
    
    # Signal khi click - đổi tên để tránh xung đột
    back_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Khởi tạo button quay về - dấu gạch ngang theo Figma"""
        # Set style trực tiếp cho back button - nhỏ đi một nửa
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: 1px solid white;
                border-radius: 6px;
                min-width: 22px;
                min-height: 22px;
                font-size: 12px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
                border: 1px solid #FFD700;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        self.setText("←")  # Mũi tên trái đẹp hơn
        self.setFixedSize(22, 22)
        # Connect signal của QPushButton với custom signal
        super().clicked.connect(self.back_clicked.emit)


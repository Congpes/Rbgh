"""
Component nút Hủy ở góc dưới trái
"""

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class CancelButton(QPushButton):
    """Nút Hủy với style đặc biệt"""
    
    # Signal
    cancel_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("Hủy", parent)
        self.init_ui()
        
    def init_ui(self):
        """Khởi tạo giao diện"""
        self.setFixedSize(80, 40)
        self.setFont(QFont("Arial", 14, QFont.Bold))
        
        # Style cho nút
        self.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #333333;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
            QPushButton:pressed {
                background-color: #C0C0C0;
            }
        """)
        
        # Connect signal
        self.clicked.connect(self.cancel_clicked.emit)

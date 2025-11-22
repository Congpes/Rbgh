"""
Component hướng dẫn nhận hàng
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class PickupGuidePanel(QWidget):
    """Panel hướng dẫn nhận hàng"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Tiêu đề "Pick-up Guide" - giảm font size xuống một nửa
        title_label = QLabel("• Pick-up Guide")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))  # 48 -> 24 (giảm một nửa)
        title_label.setStyleSheet("""
            color: white;
            background: transparent;
            font-size: 24px;
            font-weight: bold;
        """)
        layout.addWidget(title_label)
        
        # Danh sách hướng dẫn - giảm font size xuống một nửa
        instructions = [
            "1. Please make sure there is no foreign matter blocking the compartment door.",
            "2. Remove the items in the compartment and do not miss anything.",
            "3. Please tap the [Close the Door and Return] button after picking up your delivery."
        ]
        
        for instruction in instructions:
            instruction_label = QLabel(instruction)
            instruction_label.setFont(QFont("Arial", 18))  # 36 -> 18 (giảm một nửa)
            instruction_label.setStyleSheet("""
                color: white;
                background: transparent;
                font-size: 18px;
                font-weight: bold;
            """)
            instruction_label.setWordWrap(True)
            layout.addWidget(instruction_label)
        
        self.setLayout(layout)

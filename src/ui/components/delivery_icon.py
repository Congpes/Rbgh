"""
Delivery Icon Component - Icon giao hàng với text
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class DeliveryIcon(QWidget):
    """Widget hiển thị icon giao hàng với text"""
    
    # Signal khi click vào icon
    clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Khởi tạo giao diện icon giao hàng"""
        # Set style trực tiếp cho delivery icon - loại bỏ khung/viền gây khó chịu
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 12px;   /* bo đều 4 góc */
                font-size: 24px;
                min-width: 80px;
                min-height: 80px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 14px;
                background: transparent;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)  # lấp kín, tránh mép tạo cảm giác khung
        
        # Button icon - hộp carton nâu theo Figma - nhỏ hơn 3/4
        self.icon_button = QPushButton("📦")
        self.icon_button.setFixedSize(75, 75)
        self.icon_button.clicked.connect(self.clicked.emit)
        layout.addWidget(self.icon_button)
        
        # Text label - KHÔNG thêm vào layout, để ngoài
        self.text_label = QLabel("Giao Hàng")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setFont(QFont("Arial", 12, QFont.Bold))
        # KHÔNG add vào layout
        
        self.setLayout(layout)


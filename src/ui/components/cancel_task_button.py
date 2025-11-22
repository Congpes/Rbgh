"""
Component nút Cancel task ở góc trên trái
"""

from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPainter, QColor, QBrush

class CancelTaskButton(QWidget):
    """Nút Cancel task với chấm tròn xanh ngọc"""
    
    # Signal
    cancel_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Chấm tròn xanh ngọc
        self.dot_widget = QWidget()
        self.dot_widget.setFixedSize(12, 12)
        self.dot_widget.setStyleSheet("""
            QWidget {
                background-color: #31C7E9;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.dot_widget)
        
        # Text "Cancel task"
        self.cancel_label = QLabel("Cancel task")
        self.cancel_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.cancel_label.setStyleSheet("""
            color: white;
            background: transparent;
        """)
        layout.addWidget(self.cancel_label)
        
        self.setLayout(layout)
        
        # Tạo nút ẩn để xử lý click
        self.click_area = QPushButton()
        self.click_area.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
            }
        """)
        self.click_area.clicked.connect(self.cancel_clicked.emit)
        
        # Đặt nút ẩn lên trên toàn bộ widget
        self.click_area.setParent(self)
        self.click_area.setGeometry(0, 0, self.width(), self.height())
        
    def resizeEvent(self, event):
        """Cập nhật kích thước nút ẩn khi widget thay đổi"""
        super().resizeEvent(event)
        if hasattr(self, 'click_area'):
            self.click_area.setGeometry(0, 0, self.width(), self.height())

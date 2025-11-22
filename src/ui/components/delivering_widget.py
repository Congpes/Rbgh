"""
Component hiển thị vòng tròn loading "Delivering" với animation xoay
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush

class DeliveringWidget(QWidget):
    """Widget hiển thị vòng tròn loading với animation xoay"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rotation_angle = 0
        self.init_ui()
        self.setup_animation()
        
    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label "Delivering" - màu trắng để hiển thị trên nền xanh
        self.delivering_label = QLabel("Delivering")
        self.delivering_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.delivering_label.setAlignment(Qt.AlignCenter)
        self.delivering_label.setStyleSheet("""
            color: white;
            margin: 0px;
            background: transparent;
        """)
        layout.addWidget(self.delivering_label)
        
        self.setLayout(layout)
        self.setMinimumSize(200, 200)
        
    def setup_animation(self):
        """Thiết lập animation xoay"""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_rotation)
        self.animation_timer.start(50)  # 50ms = 20 FPS
        
    def update_rotation(self):
        """Cập nhật góc xoay"""
        self.rotation_angle = (self.rotation_angle + 5) % 360
        self.update()
        
    def paintEvent(self, event):
        """Vẽ vòng tròn loading với nền full và vòng xoay màu trắng"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Kích thước và vị trí
        rect = self.rect()
        center_x = rect.width() // 2
        center_y = rect.height() // 2
        radius = min(center_x, center_y) - 20
        
        # Vẽ nền full với màu nền (#1C1492)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#1C1492")))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # Vẽ loading arc (màu trắng) xoay trên nền
        painter.setPen(QPen(QColor("white"), 8, Qt.SolidLine, Qt.RoundCap))
        
        # Tính toán góc cho loading arc (xoay liên tục)
        start_angle = -90 + self.rotation_angle
        span_angle = 270  # 3/4 vòng tròn
        
        painter.drawArc(center_x - radius, center_y - radius, radius * 2, radius * 2,
                       start_angle * 16, span_angle * 16)
        
    def start_animation(self):
        """Bắt đầu animation"""
        if not self.animation_timer.isActive():
            self.animation_timer.start(50)
            
    def stop_animation(self):
        """Dừng animation"""
        self.animation_timer.stop()

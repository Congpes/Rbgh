"""
Màn hình chờ - Robot chuẩn bị và di chuyển đến phòng
Hiển thị với layout mới theo thiết kế Figma
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFrame, QProgressBar, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont, QMovie, QPainter, QColor, QPen, QBrush, QLinearGradient, QPalette

# Import components
from src.ui.components.room_info_widget import RoomInfoWidget
from src.ui.components.delivering_widget import DeliveringWidget
from src.ui.components.cancel_button import CancelButton


class WaitingScreen(QWidget):
    """Màn hình chờ với layout mới theo thiết kế Figma"""
    
    # Signals
    next_screen = pyqtSignal()
    cancel_screen = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.order_data = None
        self.waiting_time = 10000  # 10 giây cố định
        self.init_ui()
        self.setup_timers()
        
    def init_ui(self):
        """Khởi tạo giao diện theo thiết kế Figma"""
        # Set background color #1C1492
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#1C1492"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top section - Room info với khoảng cách từ trên
        self.room_info_widget = RoomInfoWidget()
        # Thêm khoảng cách từ trên
        top_spacer = QWidget()
        top_spacer.setFixedHeight(60)  # Khoảng cách 60px từ trên
        main_layout.addWidget(top_spacer)
        main_layout.addWidget(self.room_info_widget, 0, Qt.AlignTop)
        
        # Center section - Delivering widget
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setContentsMargins(50, 50, 50, 50)
        
        self.delivering_widget = DeliveringWidget()
        center_layout.addWidget(self.delivering_widget, 0, Qt.AlignCenter)
        
        center_widget = QWidget()
        center_widget.setLayout(center_layout)
        main_layout.addWidget(center_widget, 1)
        
        # Bottom section - (ẩn nút Cancel theo yêu cầu)
        # Giữ placeholder để layout không bị dịch chuyển nếu cần
        bottom_widget = QWidget()
        bottom_widget.setFixedHeight(0)
        main_layout.addWidget(bottom_widget, 0, Qt.AlignBottom)
        
        self.setLayout(main_layout)
        
        
    def setup_timers(self):
        """Thiết lập timers"""
        # Timer cho 10 giây chờ
        self.waiting_timer = QTimer()
        self.waiting_timer.timeout.connect(self.complete_waiting)
        self.waiting_timer.setSingleShot(True)
        
    def start_waiting(self):
        """Bắt đầu quá trình chờ 10 giây"""
        # Bắt đầu animation xoay
        self.delivering_widget.start_animation()
        
        # Bắt đầu timer 10 giây
        self.waiting_timer.start(self.waiting_time)
        
    def complete_waiting(self):
        """Hoàn thành thời gian chờ, chuyển sang màn hình tiếp theo"""
        # Dừng animation
        self.delivering_widget.stop_animation()
        
        # Chuyển sang màn hình tiếp theo
        self.next_screen.emit()
        
    def cancel_order(self):
        """Hủy đơn hàng"""
        # Dừng timer chờ
        self.waiting_timer.stop()
        
        # Dừng animation
        self.delivering_widget.stop_animation()
        
        # Chuyển về màn hình setup delivery
        self.cancel_screen.emit()
        
    def set_order_data(self, order_data):
        """Set dữ liệu đơn hàng"""
        # Dừng timer cũ trước
        self.reset()
        
        self.order_data = order_data
        
        # Cập nhật số phòng nếu có
        if order_data and "room" in order_data:
            room_id = order_data["room"].get("id", "314")
            self.room_info_widget.set_room_number(room_id)
        else:
            self.room_info_widget.set_room_number("314")
            
        # Tự động bắt đầu chờ 10 giây
        QTimer.singleShot(1000, self.start_waiting)
        
    def reset(self):
        """Reset về trạng thái ban đầu"""
        # Dừng timer chờ
        if self.waiting_timer.isActive():
            self.waiting_timer.stop()
            
        # Dừng animation
        self.delivering_widget.stop_animation()
                
        # Reset values
        self.order_data = None
        
        # Reset UI
        self.room_info_widget.set_room_number("314")
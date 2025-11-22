"""
Clock Widget - Hiển thị thời gian và ngày tháng
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
from datetime import datetime

class ClockWidget(QWidget):
    """Widget hiển thị đồng hồ và ngày tháng"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.start_timer()
        
    def init_ui(self):
        """Khởi tạo giao diện đồng hồ"""
        # Set style trực tiếp cho đồng hồ - loại bỏ thuộc tính không hỗ trợ
        self.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                background: transparent;
            }
            QLabel#timeLabel {
                font-size: 64px;
                font-family: "Arial", sans-serif;
            }
            QLabel#dateLabel {
                font-size: 20px;
                font-family: "Arial", sans-serif;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(5)
        
        # Label hiển thị giờ
        self.time_label = QLabel()
        self.time_label.setObjectName("timeLabel")
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)
        
        # Label hiển thị ngày
        self.date_label = QLabel()
        self.date_label.setObjectName("dateLabel")
        self.date_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.date_label)
        
        self.setLayout(layout)
        self.update_time()
        
    def start_timer(self):
        """Bắt đầu timer cập nhật thời gian"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Cập nhật mỗi giây
        
    def update_time(self):
        """Cập nhật thời gian hiển thị"""
        now = datetime.now()
        
        # Hiển thị giờ:phút
        time_str = now.strftime("%H:%M")
        self.time_label.setText(time_str)
        
        # Hiển thị ngày tháng theo format: Thu. 2025.10.4
        weekday = now.strftime("%a.")  # Thu.
        date_str = now.strftime("%Y.%m.%d")  # 2025.10.4
        self.date_label.setText(f"{weekday}\n{date_str}")


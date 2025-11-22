"""
Màn hình biểu cảm của robot
Hiển thị các trạng thái cảm xúc: vui, buồn, bình thường, chờ...
"""

import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPainter, QPen, QBrush, QColor
from PyQt5.QtCore import QRect

class EmotionScreen(QWidget):
    """Màn hình biểu cảm của robot"""
    
    # Signal để chuyển màn hình
    next_screen = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.emotions = (
            ["happy"] * 5 +  # Ưu tiên cười nhiều hơn
            ["sad", "neutral", "thinking", "sleeping", "hungry", "excited", "peaceful"]
        )
        self.current_emotion = "happy"
        self.init_ui()
        self.setup_random_emotion_timer()
        
    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)

        self.emotion_label = QLabel()
        self.emotion_label.setAlignment(Qt.AlignCenter)
        self.update_emotion_display()
        layout.addWidget(self.emotion_label, 1)

        layout.addStretch(1)

        # Thanh nút dưới cùng bên phải
        bottom_bar = QHBoxLayout()
        bottom_bar.addStretch()
        self.start_btn = QPushButton(" Bắt đầu")
        self.start_btn.setFixedSize(180, 38)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                font-size: 14px;
                font-weight: bold;
                padding: 6px 18px;
                border-radius: 10px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.start_btn.clicked.connect(self.start_delivery)
        bottom_bar.addWidget(self.start_btn)
        layout.addLayout(bottom_bar)

        self.setLayout(layout)
        from PyQt5.QtGui import QPalette
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(pal)
        self.setAutoFillBackground(True)

        self.emotion_overlay = EmotionOverlay(self)
        self.emotion_overlay.setGeometry(self.rect())
        self.emotion_overlay.lower()            
        self.start_btn.raise_()                  
        self.emotion_label.setVisible(False)
        
    def setup_random_emotion_timer(self):
        self.random_timer = QTimer(self)
        self.random_timer.timeout.connect(self.set_random_emotion)
        self.random_timer.start(5000)  # Đổi biểu cảm mỗi 5 giây

    def set_random_emotion(self):
        prev = self.current_emotion
        available = [e for e in self.emotions if e != prev]
        self.current_emotion = random.choice(available)
        self.update_emotion_display()

    def update_emotion_display(self):
        emotion_map = {
            "happy": "😊",
            "sad": "😢",
            "neutral": "😐",
            "thinking": "🤔",
            "sleeping": "😴",
            "hungry": "😋",
            "excited": "🥳",
            "peaceful": "😌"
        }
        
        emoji = emotion_map.get(self.current_emotion, "😊")
        self.emotion_label.setText(emoji)
        self.emotion_label.setStyleSheet("""
            QLabel {
                font-size: 320px;
                padding: 0px;
            }
        """)
        
    def start_delivery(self):
        """Bắt đầu quy trình giao đồ ăn"""
        print(f"Bắt đầu giao đồ ăn với biểu cảm: {self.current_emotion}")
        self.next_screen.emit()  # Phát signal để chuyển màn hình
        
    def reset(self):
        """Reset về trạng thái ban đầu"""
        self.current_emotion = "happy"
        self.update_emotion_display()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'emotion_overlay') and self.emotion_overlay is not None:
            self.emotion_overlay.setGeometry(self.rect())


class EmotionOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAutoFillBackground(False)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)  # hiệu ứng pixel
        color = QColor(0, 230, 230)
        p.setPen(QPen(color, 10, cap=Qt.SquareCap))
        p.setBrush(QBrush(color))

        w = self.width()
        h = self.height()

        # Tham số tỷ lệ để co giãn theo kích thước màn hình
        eye_r = max(20, int(min(w, h) * 0.08))
        eye_y = int(h * 0.35)
        eye_offset_x = int(w * 0.25)

        # Vẽ mắt
        p.drawEllipse(QRect(eye_offset_x - eye_r//2, eye_y - eye_r//2, eye_r, eye_r))
        p.drawEllipse(QRect(w - eye_offset_x - eye_r//2, eye_y - eye_r//2, eye_r, eye_r))

        # Vẽ miệng dạng chữ U đơn giản
        mouth_w = int(w * 0.35)
        mouth_h = int(h * 0.12)
        mouth_y = int(h * 0.60)
        arc_rect = QRect(w//2 - mouth_w//2, mouth_y - mouth_h//2, mouth_w, mouth_h)
        # Vẽ nửa dưới (chữ U) – cung 180° từ trái sang phải
        p.drawArc(arc_rect, 0, -180 * 16)
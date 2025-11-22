"""
Component thông tin giao hàng bên phải
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class DeliveryInfoPanel(QWidget):
    """Panel thông tin giao hàng và nút mở tủ"""
    
    # Signal
    open_door_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_room = None
        self.is_close_mode = False
        self.init_ui()
        
    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Label "Arrived at XXX" - căn giữa
        self.arrived_label = QLabel("Arrived at 103")
        self.arrived_label.setFont(QFont("Arial", 36, QFont.Bold))
        self.arrived_label.setAlignment(Qt.AlignCenter)  # Căn giữa
        self.arrived_label.setStyleSheet("""
            color: white;
            background: transparent;
            font-size: 36px;
            font-weight: bold;
        """)
        layout.addWidget(self.arrived_label)
        
        # Label hướng dẫn - căn giữa
        self.instruction_label = QLabel("Please pick up the delivery as soon as possible")
        self.instruction_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.instruction_label.setAlignment(Qt.AlignCenter)  # Căn giữa
        self.instruction_label.setStyleSheet("""
            color: white;
            background: transparent;
            font-size: 24px;
            font-weight: bold;
        """)
        self.instruction_label.setWordWrap(True)
        layout.addWidget(self.instruction_label)
        
        # Spacer để đẩy nút xuống dưới
        layout.addStretch()
        
        # Nút "Open the door to pick up" - bo tròn đẹp hơn
        self.open_door_btn = QPushButton("Open the door to pick up")
        self.open_door_btn.setFont(QFont("Arial", 18, QFont.Bold))
        self.open_door_btn.setMinimumHeight(70)
        self.open_door_btn.setStyleSheet("""
            QPushButton {
                background-color: #31C7E9;
                color: white;
                border: none;
                border-radius: 35px;
                padding: 20px 30px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2BB5D8;
                transform: scale(1.02);
            }
            QPushButton:pressed {
                background-color: #26A3C4;
                transform: scale(0.98);
            }
        """)
        self.open_door_btn.clicked.connect(self.open_door_clicked.emit)
        layout.addWidget(self.open_door_btn)
        
        self.setLayout(layout)
        
    def set_room_number(self, room_number):
        """Cập nhật số phòng"""
        self.current_room = room_number
        self.arrived_label.setText(f"Arrived at {room_number}")
        
    def set_open_door_enabled(self, enabled):
        """Bật/tắt nút mở tủ"""
        self.open_door_btn.setEnabled(enabled)
        if enabled:
            self.open_door_btn.setStyleSheet("""
                QPushButton {
                    background-color: #31C7E9;
                    color: white;
                    border: none;
                    border-radius: 30px;
                    padding: 15px 25px;
                }
                QPushButton:hover {
                    background-color: #2BB5D8;
                }
                QPushButton:pressed {
                    background-color: #26A3C4;
                }
            """)
        else:
            self.open_door_btn.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    color: #CCCCCC;
                    border: none;
                    border-radius: 35px;
                    padding: 20px 30px;
                    font-weight: bold;
                }
            """)

    def set_mode_open(self):
        """Đặt nút về trạng thái mở tủ."""
        self.is_close_mode = False
        self.open_door_btn.setText("Open the door to pick up")

    def set_mode_close(self):
        """Đặt nút về trạng thái đóng tủ và quay lại."""
        self.is_close_mode = True
        self.open_door_btn.setText("Close the door and return")

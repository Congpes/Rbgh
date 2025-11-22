"""
Màn hình lấy đồ - Hiển thị khi robot đã đến nơi và chờ người dùng lấy đồ
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFrame, QTextEdit, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor

# Import components
from src.ui.components.cancel_task_button import CancelTaskButton
from src.ui.components.cabinet_status_panel import CabinetStatusPanel
from src.ui.components.delivery_info_panel import DeliveryInfoPanel
from src.ui.components.pickup_guide_panel import PickupGuidePanel

class PickupScreen(QWidget):
    """Màn hình lấy đồ với layout mới theo thiết kế Figma"""
    
    # Signals
    done = pyqtSignal()
    report_issue = pyqtSignal()
    cancel_task = pyqtSignal()
    opened = pyqtSignal()   # mở tủ xong
    closed = pyqtSignal()   # đóng tủ xong

    def __init__(self):
        super().__init__()
        self.order_data = None
        self.current_room = None
        self.delivery_cabinets = []
        self.active_mode = False
        self.spinner_timer = None
        self.spinner_index = 0
        self.init_ui()

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

        # Top bar - Cancel task button
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(20, 20, 20, 10)
        
        self.cancel_task_btn = CancelTaskButton()
        self.cancel_task_btn.cancel_clicked.connect(self.cancel_task.emit)
        top_layout.addWidget(self.cancel_task_btn, 0, Qt.AlignLeft)
        top_layout.addStretch()
        
        self.top_widget = QWidget()
        self.top_widget.setLayout(top_layout)
        main_layout.addWidget(self.top_widget, 0, Qt.AlignTop)
        
        # Main content area
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(20, 10, 20, 10)
        content_layout.setSpacing(30)
        
        # Left side - Cabinet status panel
        self.cabinet_panel = CabinetStatusPanel()
        self.cabinet_panel.cabinet_clicked.connect(self.on_cabinet_clicked)
        content_layout.addWidget(self.cabinet_panel, 0)
        
        # Right side - Delivery info panel
        self.delivery_info_panel = DeliveryInfoPanel()
        self.delivery_info_panel.open_door_clicked.connect(self.on_open_door_clicked)
        content_layout.addWidget(self.delivery_info_panel, 1)
        
        self.content_widget = QWidget()
        self.content_widget.setLayout(content_layout)
        main_layout.addWidget(self.content_widget, 1)
        
        # Bottom - Pickup guide panel
        self.pickup_guide_panel = PickupGuidePanel()
        main_layout.addWidget(self.pickup_guide_panel, 0, Qt.AlignBottom)

        # Active (minimal) container – chỉ hiển thị spinner + message
        self.active_container = QWidget()
        active_v = QVBoxLayout()
        active_v.setContentsMargins(0, 0, 0, 0)
        active_v.setSpacing(10)
        active_v.setAlignment(Qt.AlignCenter)

        active_row = QHBoxLayout()
        active_row.setAlignment(Qt.AlignCenter)
        active_row.setSpacing(16)

        self.spinner_label = QLabel("…")
        self.spinner_label.setStyleSheet("color:white;background:transparent; font-size: 38px; font-weight: bold;")
        self.spinner_label.setFont(QFont("Arial", 38, QFont.Bold))

        self.active_text_label = QLabel("Compartment opening. Please wait ...")
        self.active_text_label.setStyleSheet("color:white;background:transparent; font-size: 38px; font-weight: bold;")
        self.active_text_label.setFont(QFont("Arial", 38, QFont.Bold))

        active_row.addWidget(self.spinner_label)
        active_row.addWidget(self.active_text_label)
        active_v.addLayout(active_row)
        self.active_container.setLayout(active_v)
        self.active_container.hide()
        main_layout.addWidget(self.active_container, 1)
        
        self.setLayout(main_layout)

    # ===== Active cabinet helpers =====
    def _start_spinner(self):
        frames = ["·  ", "·· ", "···", " ··", "  ·", "   "]
        # Lưu frames vào thuộc tính để dùng trong timer
        self._spinner_frames = frames
        if self.spinner_timer is None:
            self.spinner_timer = QTimer(self)
            self.spinner_timer.timeout.connect(self._tick_spinner)
        self.spinner_index = 0
        self.spinner_timer.start(120)

    def _tick_spinner(self):
        frame = self._spinner_frames[self.spinner_index % len(self._spinner_frames)]
        self.spinner_label.setText(frame)
        self.spinner_index += 1

    def _stop_spinner(self):
        if self.spinner_timer:
            self.spinner_timer.stop()
        self.spinner_label.setText("")

    def set_active_message(self, text: str):
        """Bật chế độ active: chỉ hiển thị text + spinner ở giữa."""
        self.active_mode = True
        self.top_widget.hide()
        self.content_widget.hide()
        self.pickup_guide_panel.hide()
        self.active_text_label.setText(text)
        self.active_container.show()
        self._start_spinner()

    def restore_normal(self):
        """Hiện lại nút và nội dung bình thường."""
        self._stop_spinner()
        self.active_container.hide()
        self.top_widget.show()
        self.content_widget.show()
        self.pickup_guide_panel.show()
        self.active_mode = False

    def on_cabinet_clicked(self, cabinet_id):
        """Xử lý khi click vào tủ"""
        print(f"Cabinet clicked: {cabinet_id}")
        
    def on_open_door_clicked(self):
        # Không dùng trong vai trò active_cabinet
        pass

    def start_opening(self):
        """Bắt đầu hiển thị chờ mở tủ 3s."""
        self.set_active_message("Compartment opening. Please wait ...")
        QTimer.singleShot(3000, self._emit_opened)

    def start_closing(self):
        """Bắt đầu hiển thị chờ đóng tủ 3s."""
        self.set_active_message("Compartment closing. Please wait ...")
        QTimer.singleShot(3000, self._emit_closed)

    def _emit_opened(self):
        self.restore_normal()
        self.opened.emit()

    def _emit_closed(self):
        self.restore_normal()
        self.closed.emit()
        
    def set_order_data(self, order_data):
        """Set dữ liệu đơn hàng và cập nhật UI"""
        self.order_data = order_data
        
        if order_data and "room" in order_data and "cabinets" in order_data:
            room_id = order_data["room"]["id"]
            cabinets = order_data["cabinets"]
            
            # Lấy danh sách tủ có đồ cho phòng này
            delivery_cabinets = []
            for cabinet in cabinets:
                if cabinet.get("assigned_room_id") == room_id:
                    delivery_cabinets.append(cabinet["id"])
            
            self.current_room = room_id
            self.delivery_cabinets = delivery_cabinets
            
            # Cập nhật UI
            self.cabinet_panel.update_for_room(room_id, delivery_cabinets)
            self.delivery_info_panel.set_room_number(room_id)
            
            # Bật nút mở tủ nếu có tủ chứa đồ
            has_delivery = len(delivery_cabinets) > 0
            self.delivery_info_panel.set_open_door_enabled(has_delivery)
            
    def reset(self):
        """Reset về trạng thái ban đầu"""
        self.order_data = None
        self.current_room = None
        self.delivery_cabinets = []
        
        # Reset UI
        self.cabinet_panel.update_for_room("103", [])
        self.delivery_info_panel.set_room_number("103")
        self.delivery_info_panel.set_open_door_enabled(False)
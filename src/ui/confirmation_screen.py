"""
Màn hình xác nhận - Robot đã đến phòng và chờ khách lấy hàng
Thiết kế theo hình mẫu với giao diện đơn giản, hiện đại
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFrame, QSizePolicy, QSpacerItem)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QUrl
from PyQt5.QtGui import QFont, QPalette, QLinearGradient, QBrush, QColor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import os

# Import components
from src.ui.components.cancel_task_button import CancelTaskButton
from src.ui.components.cabinet_status_panel import CabinetStatusPanel
from src.ui.components.delivery_info_panel import DeliveryInfoPanel
from src.ui.components.pickup_guide_panel import PickupGuidePanel

class ConfirmationScreen(QWidget):
    """Màn hình xác nhận robot đã đến"""
    
    # Signals
    restart_screen = pyqtSignal()  # Về emotion screen để bắt đầu mới
    home_screen = pyqtSignal()     # Về trang chủ
    confirmed = pyqtSignal()      # <-- PHẢI là signal, KHÔNG phải function
    items_picked = pyqtSignal()   # Khi người dùng xác nhận đã lấy đồ
    cancelled = pyqtSignal()      # Khi người dùng hủy đơn
    phone_call_started = pyqtSignal(str)  # Gửi số điện thoại khi bắt đầu gọi
    phone_call_stopped = pyqtSignal()     # Khi dừng cuộc gọi
    open_cabinet = pyqtSignal()           # Yêu cầu mở tủ
    close_cabinet = pyqtSignal()          # Yêu cầu đóng tủ
    
    def __init__(self):
        super().__init__()
        self.delivery_summary = {}
        self.current_room = None
        self.delivery_cabinets = []
        self.phone_call_active = False
        self.phone_call_timer = None
        self.phone_call_duration = 10000  # 10 giây mỗi cuộc gọi
        self.phone_call_count = 0
        self.max_phone_calls = 3
        self.media_player = QMediaPlayer()
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
        self.cancel_task_btn.cancel_clicked.connect(self.on_cancel_clicked)
        top_layout.addWidget(self.cancel_task_btn, 0, Qt.AlignLeft)
        top_layout.addStretch()
        
        top_widget = QWidget()
        top_widget.setLayout(top_layout)
        main_layout.addWidget(top_widget, 0, Qt.AlignTop)
        
        # Main content area - chia đôi 1/2 - 1/2
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(20, 10, 20, 20)
        content_layout.setSpacing(20)
        
        # Left side - Cabinet (1/2) - khung y hệt setup_delivery
        left_panel = QVBoxLayout()
        left_panel.setSpacing(20)
        
        # Cabinet status panel - chiếm toàn bộ không gian
        self.cabinet_panel = CabinetStatusPanel()
        self.cabinet_panel.cabinet_clicked.connect(self.on_cabinet_clicked)
        left_panel.addWidget(self.cabinet_panel, 1)
        
        # Pickup guide panel
        self.pickup_guide_panel = PickupGuidePanel()
        left_panel.addWidget(self.pickup_guide_panel, 0)
        
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        content_layout.addWidget(left_widget, 1)  # 1/2 không gian
        
        # Right side - Delivery Info Panel (1/2)
        right_panel = QVBoxLayout()
        right_panel.setAlignment(Qt.AlignTop)
        right_panel.setSpacing(20)
        
        # Delivery info panel - chiếm toàn bộ không gian
        self.delivery_info_panel = DeliveryInfoPanel()
        self.delivery_info_panel.open_door_clicked.connect(self.on_open_door_clicked)
        right_panel.addWidget(self.delivery_info_panel, 1)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        content_layout.addWidget(right_widget, 1)  # 1/2 không gian
        
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget, 1)
        
        # Phone call status label - ẩn hoàn toàn
        self.phone_status_label = QLabel("📞 Gọi điện cho khách")
        self.phone_status_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.phone_status_label.setStyleSheet("""
            color: white;
            background: transparent;
            padding: 10px;
        """)
        self.phone_status_label.setAlignment(Qt.AlignCenter)
        self.phone_status_label.hide()  # Ẩn hoàn toàn
        
        self.setLayout(main_layout)
        
    def on_cabinet_clicked(self, cabinet_id):
        """Xử lý khi click vào tủ"""
        print(f"Cabinet clicked: {cabinet_id}")
        
    def on_open_door_clicked(self):
        """Xử lý khi click nút mở tủ"""
        print("Open door clicked")
        # Nếu panel đang ở chế độ đóng thì emit close, ngược lại emit open
        if self.delivery_info_panel.is_close_mode:
            self.close_cabinet.emit()
        else:
            self.open_cabinet.emit()

    def set_delivery_summary(self, summary):
        """Set thông tin giao hàng và cập nhật UI"""
        self.delivery_summary = summary
        
        if "room_info" in summary and "cabinets" in summary:
            room_info = summary["room_info"]
            cabinets = summary["cabinets"]
            room_id = room_info.get("name", "103").replace("Phòng ", "")
            
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
            self.delivery_info_panel.set_mode_open()
            
            # Bật nút mở tủ nếu có tủ chứa đồ
            has_delivery = len(delivery_cabinets) > 0
            self.delivery_info_panel.set_open_door_enabled(has_delivery)
        
        # Tự động bắt đầu gọi điện sau 1 giây - TẠM THỜI VÔ HIỆU HÓA
        # QTimer.singleShot(1000, self.start_auto_phone_calls)

    def start_auto_phone_calls(self):
        """Bắt đầu tự động gọi điện 3 lần"""
        self.phone_call_count = 0
        self.make_phone_call()
        
    def make_phone_call(self):
        """Thực hiện gọi điện thoại"""
        if self.phone_call_count >= self.max_phone_calls:
            # Đã gọi đủ 3 lần, bỏ qua phòng này
            self.handle_no_response()
            return
            
        self.phone_call_count += 1
        
        # Lấy số điện thoại từ room info
        phone_number = "101"  # Default
        if self.delivery_summary and "room_info" in self.delivery_summary:
            room_info = self.delivery_summary["room_info"]
            phone_number = room_info.get("phone", "101")
        
        # Cập nhật UI
        self.phone_call_active = True
        self.phone_status_label.setText(f"📞 Đang gọi phòng {phone_number}... (Lần {self.phone_call_count}/3)")
        self.phone_status_label.show()
        
        # Bắt đầu timer cho cuộc gọi
        self.phone_call_timer = QTimer()
        self.phone_call_timer.timeout.connect(self.phone_call_timeout)
        self.phone_call_timer.setSingleShot(True)
        self.phone_call_timer.start(self.phone_call_duration)
        
        # Emit signal để main window có thể xử lý
        self.phone_call_started.emit(phone_number)
        
        # Tự động phát âm thanh sau 2 giây kể từ khi bắt đầu gọi
        QTimer.singleShot(2000, self._auto_play_accept_sound)
        
    def phone_call_timeout(self):
        """Xử lý khi cuộc gọi hết thời gian"""
        if not self.phone_call_active:
            return
            
        # Cập nhật UI
        self.phone_call_active = False
        self.phone_status_label.setText(f"📞 Cuộc gọi lần {self.phone_call_count} đã kết thúc")
        
        # Gọi lần tiếp theo sau 2 giây
        QTimer.singleShot(2000, self.make_phone_call)
        
    def handle_no_response(self):
        """Xử lý khi không có phản hồi sau 3 lần gọi"""
        self.phone_call_active = False
        self.phone_status_label.setText("❌ Không có phản hồi từ phòng")
        
        # Emit signal để main window xử lý (bỏ qua phòng này)
        self.phone_call_stopped.emit()
        
    def stop_phone_call(self):
        """Dừng cuộc gọi điện thoại (khách bấm dừng)"""
        if not self.phone_call_active:
            return
            
        # Dừng timer
        if self.phone_call_timer:
            self.phone_call_timer.stop()
            self.phone_call_timer = None
            
        # Cập nhật UI
        self.phone_call_active = False
        self.phone_status_label.setText("📞 Cuộc gọi đã dừng")
        
        # Emit signal
        self.phone_call_stopped.emit()

    def on_confirm_clicked(self):
        """Xử lý khi người dùng bấm xác nhận đã lấy đồ"""
        # Dừng cuộc gọi nếu đang gọi
        if self.phone_call_active:
            self.stop_phone_call()
            
        # Emit cả hai signal
        self.items_picked.emit()
        self.confirmed.emit()
    
    def on_cancel_clicked(self):
        """Xử lý khi người dùng bấm hủy đơn"""
        # Dừng cuộc gọi nếu đang gọi
        if self.phone_call_active:
            self.stop_phone_call()
            
        # Emit signal hủy
        self.cancelled.emit()
    
    def reset(self):
        """Reset về trạng thái ban đầu"""
        # Dừng cuộc gọi nếu đang gọi
        if self.phone_call_active:
            self.stop_phone_call()
            
        self.delivery_summary = {}
        self.current_room = None
        self.delivery_cabinets = []
        self.phone_call_count = 0
        
        # Reset UI
        self.cabinet_panel.update_for_room("103", [])
        self.delivery_info_panel.set_room_number("103")
        self.delivery_info_panel.set_open_door_enabled(False)

    def _auto_play_accept_sound(self):
        """Phát âm thanh tự động sau khi bắt đầu gọi (nếu vẫn đang gọi)."""
        if self.phone_call_active:
            self._play_accept_sound()

    def _play_accept_sound(self):
        try:
            # Tìm file trong assets/sounds/nhanhang.mp3 (relative to project root)
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            sound_path = os.path.join(base_dir, 'assets', 'sounds', 'nhanhang.mp3')
            if os.path.exists(sound_path):
                url = QUrl.fromLocalFile(sound_path)
                self.media_player.setMedia(QMediaContent(url))
                self.media_player.setVolume(100)
                self.media_player.play()
        except Exception as _:
            pass
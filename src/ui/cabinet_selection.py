"""
Màn hình chọn tủ đồ ăn
Hiển thị 3 tủ: trái, phải, dưới với trạng thái và dung lượng
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFrame, QGridLayout, QProgressBar, QButtonGroup)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QRect
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor

class CabinetSelectionScreen(QWidget):
    """Màn hình chọn tủ đồ ăn"""
    
    # Signals
    next_screen = pyqtSignal(str)  # Truyền cabinet_id được chọn để chuyển sang chọn phòng
    back_screen = pyqtSignal()
    # add_more = pyqtSignal(str)   # Không dùng nữa: xác nhận tủ này và tiếp tục chọn thêm tủ
    go_waiting = pyqtSignal(str)   # Xác nhận tủ này và đi thẳng sang chờ
    remove_cabinet = pyqtSignal(str)  # Xóa tủ đã lưu để làm lại theo từng tủ
    clear_all = pyqtSignal()       # Xóa dữ liệu tủ đã lưu để làm lại
    
    def __init__(self):
        super().__init__()
        self.selected_cabinet = None
        self.room_info = None
        self.cabinet_data = self.load_cabinet_data()
        self.locked_cabinet_ids = set()  # các tủ đã lưu, không cho chọn nữa
        self.init_ui()
        self.setup_status_timer()
        
    def load_cabinet_data(self):
        """Load thông tin tủ đồ ăn (tạm thời hardcode)"""
        return {
            "left": {
                "name": "Tủ Trái",
                "position": "Bên trái robot",
                "capacity": 10,
                "current_items": 7,
                "temperature": 4,  # Celsius
                "status": "ready",  # ready, busy, error, empty
                "icon": "📦",
                "color": "#2196F3"
            },
            "right": {
                "name": "Tủ Phải", 
                "position": "Bên phải robot",
                "capacity": 10,
                "current_items": 5,
                "temperature": 6,
                "status": "ready",
                "icon": "📦",
                "color": "#4CAF50"
            },
            "bottom": {
                "name": "Tủ Dưới",
                "position": "Dưới robot", 
                "capacity": 15,
                "current_items": 12,
                "temperature": 2,
                "status": "ready",
                "icon": "📦", 
                "color": "#FF9800"
            }
        }
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Header: giữ tiêu đề và span thông tin đã chọn, bỏ "Bước x/8"
        self.header_widget = self.create_header()
        layout.addWidget(self.header_widget)

        self.cabinet_container = self.create_cabinet_area()
        layout.addWidget(self.cabinet_container, 1)

        self.footer_widget = self.create_footer()
        layout.addWidget(self.footer_widget)

        self.setLayout(layout)
        
    def create_header(self):
        """Tạo header"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("""
            QFrame {
                background-color: #9C27B0;
                border-radius: 10px;
                margin: 10px;
            }
            QLabel {
                color: white;
                font-weight: bold;
                padding: 15px;
            }
        """)
        
        layout = QHBoxLayout()
        
        # Title
        title = QLabel("📦 Chọn Tủ Đồ Ăn")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Selected display
        self.selected_display = QLabel("Chưa chọn tủ")
        self.selected_display.setStyleSheet("background-color: rgba(255,255,255,0.3); border-radius: 10px; padding: 5px 15px;")
        layout.addWidget(self.selected_display)
        
        frame.setLayout(layout)
        return frame
        
    def create_cabinet_area(self):
        """Tạo khu vực hiển thị các tủ"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                margin: 10px;
                padding: 20px;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)  # Thêm dòng này
        
        # Tạo button group cho các tủ
        self.cabinet_buttons = QButtonGroup()
        
        # Tạo các tủ
        for cabinet_id, cabinet_info in self.cabinet_data.items():
            cabinet_widget = self.create_cabinet_widget(cabinet_id, cabinet_info)
            layout.addWidget(cabinet_widget)
            
        frame.setLayout(layout)
        return frame
        
    def create_cabinet_widget(self, cabinet_id, cabinet_info):
        """Tạo widget cho từng tủ"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setFixedSize(260, 340)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {cabinet_info['color']};
                border-radius: 15px;
                margin: 5px;
            }}
            QLabel {{
                color: white;
                font-weight: bold;
            }}
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(10)

        # Icon
        icon_label = QLabel(f"{cabinet_info['icon']}")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; padding: 4px;")
        layout.addWidget(icon_label)

        # Tên tủ (nếu muốn giữ lại, nếu không thì xóa luôn)
        name_label = QLabel(cabinet_info['name'])
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(name_label)


        select_btn = QPushButton("Chọn Tủ Này")
        select_btn.setMinimumHeight(32)
        select_btn.setCheckable(True)
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,0.9);
                color: #333;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 6px;
                margin: 3px;
            }
            QPushButton:hover {
                background-color: white;
            }
            QPushButton:checked {
                background-color: #4CAF50;
                color: white;
                border: 2px solid white;
            }
        """)
        if cabinet_info['status'] != "ready" or cabinet_id in self.locked_cabinet_ids:
            select_btn.setEnabled(False)
            select_btn.setText("Đã lưu" if cabinet_id in self.locked_cabinet_ids else "Không khả dụng")
        select_btn.clicked.connect(lambda: self.select_cabinet(cabinet_id, cabinet_info))
        self.cabinet_buttons.addButton(select_btn)
        layout.addWidget(select_btn)

        # Nút xóa chỉ hiện khi tủ đã lưu
        if cabinet_id in self.locked_cabinet_ids:
            delete_btn = QPushButton("🗑️ Xóa tủ này")
            delete_btn.setMinimumHeight(28)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 6px;
                    margin: 3px;
                }
                QPushButton:hover { background-color: #c82333; }
            """)
            delete_btn.clicked.connect(lambda: self.on_delete_cabinet(cabinet_id))
            layout.addWidget(delete_btn)

        layout.addStretch()
        frame.setLayout(layout)
        return frame
        
    def create_info_panel(self):
        """Tạo panel thông tin chi tiết"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                margin: 10px;
                padding: 15px;
            }
        """)
        
        layout = QHBoxLayout()
        
        # Cabinet info
        self.info_label = QLabel("Chọn tủ để xem thông tin chi tiết và loại đồ ăn phù hợp")
        self.info_label.setStyleSheet("color: #666; font-style: italic; font-size: 14px;")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label, 2)
        
        # Suitable items display
        self.suitable_items = QLabel()
        self.suitable_items.setStyleSheet("""
            background-color: white; 
            border-radius: 10px; 
            padding: 15px; 
            border: 2px solid #e0e0e0;
        """)
        self.suitable_items.setWordWrap(True)
        layout.addWidget(self.suitable_items, 1)
        
        frame.setLayout(layout)
        return frame
        
    def create_footer(self):
        """Tạo footer"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #F2F2F2;
                border-radius: 18px;
                margin: 10px;
                padding: 18px;
            }
        """)
        
        layout = QHBoxLayout()
        
        # Back button
        back_btn = QPushButton("⬅️ Quay lại")
        back_btn.setMinimumHeight(50)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn)
        
        layout.addStretch()
        
        # Go waiting button
        self.go_waiting_btn = QPushButton(" Di chuyển")
        self.go_waiting_btn.setMinimumHeight(50)
        self.go_waiting_btn.setEnabled(False)
        self.go_waiting_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.go_waiting_btn.clicked.connect(self.confirm_go_waiting)
        layout.addWidget(self.go_waiting_btn)
        
        # Next button
        self.next_btn = QPushButton("Chọn phòng ➡️")
        self.next_btn.setMinimumHeight(50)
        self.next_btn.setEnabled(False)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.next_btn.clicked.connect(self.go_next)
        layout.addWidget(self.next_btn)
        
        frame.setLayout(layout)
        return frame
        
    def setup_status_timer(self):
        """Setup timer để cập nhật trạng thái tủ"""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_cabinet_status)
        self.status_timer.start(5000)  # Cập nhật mỗi 5 giây
        
    def select_cabinet(self, cabinet_id, cabinet_info):
        """Chọn tủ"""
        self.selected_cabinet = cabinet_id
        self.selected_cabinet_info = cabinet_info
        self.update_selection_display()
        
        print(f"Đã chọn tủ: {cabinet_info['name']} (ID: {cabinet_id})")
        
    def update_selection_display(self):
        """Cập nhật hiển thị tủ được chọn"""
        if self.selected_cabinet:
            info = self.selected_cabinet_info
            self.selected_display.setText(f"✅ {info['name']}")
            self.selected_display.setStyleSheet("""
                background-color: #4CAF50; 
                color: white;
                border-radius: 10px; 
                padding: 5px 15px;
                font-weight: bold;
            """)
            self.next_btn.setEnabled(True)
            # Chỉ bật qua chờ nếu đã có ít nhất 1 tủ được lưu
            self.update_go_waiting_enabled()
        else:
            self.selected_display.setText("Chưa chọn tủ")
            self.selected_display.setStyleSheet("""
                background-color: rgba(255,255,255,0.3); 
                border-radius: 10px; 
                padding: 5px 15px;
            """)
            self.next_btn.setEnabled(False)
            self.update_go_waiting_enabled()
            
    def update_cabinet_status(self):
        """Cập nhật trạng thái tủ (simulation)"""
        # Simulate random status changes for demo
        import random
        
        for cabinet_id, cabinet_info in self.cabinet_data.items():
            # Random chance to change items count
            if random.random() < 0.1:  # 10% chance
                change = random.randint(-1, 1)
                new_count = max(0, min(cabinet_info['capacity'], cabinet_info['current_items'] + change))
                cabinet_info['current_items'] = new_count
                
        print("Cabinet status updated")
        
    def set_room_info(self, room_id, room_info):
        """Set thông tin phòng từ màn hình trước"""
        self.room_info = {"id": room_id, "info": room_info}
        print(f"Cabinet selection for room: {room_info.get('name', room_id)}")

    def set_locked_cabinets(self, locked_ids):
        """Nhận danh sách tủ đã khóa để vô hiệu hóa chọn lại"""
        self.locked_cabinet_ids = set(locked_ids or [])
        # Chỉ rebuild khu vực tủ, giữ nguyên header/footer để tránh trắng màn
        layout = self.layout()
        if hasattr(self, 'cabinet_container') and self.cabinet_container is not None:
            self.cabinet_container.setParent(None)
        self.cabinet_container = self.create_cabinet_area()
        layout.insertWidget(1, self.cabinet_container, 1)
        self.update_go_waiting_enabled()

    def update_go_waiting_enabled(self):
        """Bật/tắt nút qua chờ tùy theo đã có tủ lưu hay chưa"""
        has_locked = len(self.locked_cabinet_ids) > 0
        if hasattr(self, 'go_waiting_btn'):
            self.go_waiting_btn.setEnabled(has_locked)
        
    def go_back(self):
        """Quay lại màn hình trước"""
        print("Quay lại màn hình chọn phòng")
        self.back_screen.emit()
        
    def go_next(self):
        """Chuyển đến màn hình tiếp theo"""
        if self.selected_cabinet:
            print(f"Chuyển đến màn hình chọn phòng - Tủ: {self.selected_cabinet}")
            self.next_screen.emit(self.selected_cabinet)

    # def confirm_add_more(self):
    #     """(Deprecated) Xác nhận tủ hiện tại và tiếp tục chọn thêm"""
    #     pass

    def confirm_go_waiting(self):
        """Xác nhận tủ và đi thẳng sang chờ"""
        # Chỉ cho phép nếu đã có ít nhất 1 tủ đã lưu
        if len(self.locked_cabinet_ids) > 0 and self.selected_cabinet:
            print(f"Xác nhận tủ và qua chờ luôn: {self.selected_cabinet}")
            self.go_waiting.emit(self.selected_cabinet)
            
    def on_delete_cabinet(self, cabinet_id: str):
        """Xóa tủ đã lưu theo từng tủ"""
        if cabinet_id in self.locked_cabinet_ids:
            # Không tự rebuild ở đây; ủy quyền cho MainWindow để đồng bộ state
            self.remove_cabinet.emit(cabinet_id)

    def on_clear_clicked(self):
        """Xóa dữ liệu các tủ đã lưu và reset màn hình"""
        self.locked_cabinet_ids = set()
        self.reset()
        # Rebuild UI
        for i in reversed(range(self.layout().count())):
            widget = self.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)
        header = self.create_header()
        self.layout().addWidget(header)
        cabinet_area = self.create_cabinet_area()
        self.layout().addWidget(cabinet_area, 1)
        footer = self.create_footer()
        self.layout().addWidget(footer)
        self.update_go_waiting_enabled()
        # Bắn signal để MainWindow dọn dữ liệu toàn cục
        self.clear_all.emit()
    def reset(self):
        """Reset về trạng thái ban đầu"""
        self.selected_cabinet = None
        # Uncheck all buttons
        for button in self.cabinet_buttons.buttons():
            button.setChecked(False)
        self.update_selection_display()
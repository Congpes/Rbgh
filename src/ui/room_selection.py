"""
Màn hình chọn phòng cần giao đồ ăn
Hiển thị danh sách phòng trong tòa nhà với sơ đồ trực quan
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFrame, QGridLayout, QScrollArea, QButtonGroup)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor

class RoomSelectionScreen(QWidget):
    """Màn hình chọn phòng"""
    
    # Signals
    next_screen = pyqtSignal(str)  # Truyền room_id được chọn
    back_screen = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.selected_room = None
        self.selected_display = QLabel("Chưa chọn phòng")  # Thêm dòng này
        self.room_data = self.load_room_data()
        self.init_ui()
        
    def load_room_data(self):
        """Load danh sách phòng (tạm thời hardcode, sau sẽ load từ JSON)"""
        return {
            "lobby": {"name": "Sảnh chính", "floor": 1, "type": "public", "phone": "101"},
            "101": {"name": "Phòng 101", "floor": 1, "type": "room", "phone": "101"}, 
            "102": {"name": "Phòng 102", "floor": 1, "type": "room", "phone": "102"},
            "103": {"name": "Phòng 103", "floor": 1, "type": "room", "phone": "103"},
            "104": {"name": "Phòng 104", "floor": 1, "type": "room", "phone": "104"},
            "201": {"name": "Phòng 201", "floor": 2, "type": "room", "phone": "201"},
            "202": {"name": "Phòng 202", "floor": 2, "type": "room", "phone": "202"},
            "203": {"name": "Phòng 203", "floor": 2, "type": "room", "phone": "203"},
            "204": {"name": "Phòng 204", "floor": 2, "type": "room", "phone": "204"},
            "301": {"name": "Phòng 301", "floor": 3, "type": "vip", "phone": "301"},
            "302": {"name": "Phòng 302", "floor": 3, "type": "vip", "phone": "302"},
            "restaurant": {"name": "Nhà hàng", "floor": 1, "type": "public", "phone": "199"},
            "meeting_room": {"name": "Phòng họp", "floor": 2, "type": "public", "phone": "299"}
        }
        
    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Header: hiển thị tiêu đề và phòng đã chọn (giống màn hình tủ)
        header = self.create_header()
        layout.addWidget(header)

        # Main content area
        content_layout = QHBoxLayout()
        
        # Floor selector (bên trái)
        floor_selector = self.create_floor_selector()
        content_layout.addWidget(floor_selector, 1)
        
        # Room grid (bên phải)
        room_area = self.create_room_area()
        content_layout.addWidget(room_area, 3)
        
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        layout.addWidget(content_widget, 1)
        
        # Footer với navigation
        footer = self.create_footer()
        layout.addWidget(footer)
        
        self.setLayout(layout)
        
    def create_header(self):
        """Tạo header"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("""
            QFrame {
                background-color: #5B2C8F;
                border-radius: 18px;
                margin: 10px;
            }
            QLabel {
                color: white;
                font-weight: bold;
                padding: 18px;
                font-size: 18px;
            }
        """)
        layout = QHBoxLayout()
        
        # Title giống Cabinet
        title = QLabel("📍 Chọn Phòng")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Hiển thị phòng đã chọn ở góc phải
        self.selected_display = QLabel("Chưa chọn phòng")
        self.selected_display.setStyleSheet("background-color: rgba(255,255,255,0.25); color: white; border-radius: 10px; padding: 8px 18px; font-weight: bold;")
        layout.addWidget(self.selected_display)
        frame.setLayout(layout)
        return frame
        
    def create_floor_selector(self):
        """Tạo bộ chọn tầng"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Floor")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 12px; background-color: #5B2C8F; color: white; border-radius: 8px; margin-bottom: 12px;")
        layout.addWidget(title)
        
        # Floor buttons
        self.floor_buttons = QButtonGroup()
        floors = [1, 2, 3]
        
        for floor in floors:
            btn = QPushButton(f"Tầng {floor}")
            btn.setMinimumHeight(60)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, f=floor: self.select_floor(f))
            
            # Count rooms on this floor
            room_count = len([r for r in self.room_data.values() if r["floor"] == floor])
            btn.setToolTip(f"Tầng {floor} - {room_count} phòng")
            
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #6FCF97;
                    color: #fff;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 14px;
                    padding: 16px 0;
                    margin-bottom: 10px;
                }
                QPushButton:checked {
                    background-color: #5B2C8F;
                    color: #fff;
                    border: 3px solid #fff;
                }
                QPushButton:hover {
                    background-color: #7B3FE4;
                }
            """)
            
            self.floor_buttons.addButton(btn, floor)
            layout.addWidget(btn)
            
        # Select floor 1 by default
        self.floor_buttons.button(1).setChecked(True)
        self.current_floor = 1
        
        layout.addStretch()
        
        frame.setLayout(layout)
        return frame
        
    def create_room_area(self):
        """Tạo khu vực hiển thị phòng"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("""
            QFrame {
                background-color: #fff;
                border-radius: 18px;
                margin: 8px;
                padding: 18px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Title
        self.room_title = QLabel(" Tầng 1 ")
        self.room_title.setFont(QFont("Arial", 14, QFont.Bold))
        self.room_title.setAlignment(Qt.AlignCenter)
        self.room_title.setStyleSheet("padding: 12px; background-color: #6FCF97; color: white; border-radius: 8px; margin-bottom: 12px;")
        layout.addWidget(self.room_title)
        
        # Scrollable room grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.room_widget = QWidget()
        self.room_layout = QGridLayout(self.room_widget)
        self.room_layout.setSpacing(10)
        
        scroll.setWidget(self.room_widget)
        layout.addWidget(scroll, 1)
        
        # Update room display
        self.update_room_display()
        
        frame.setLayout(layout)
        return frame
        
    def create_footer(self):
        """Tạo footer với navigation buttons"""
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
                background-color: #5B2C8F;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 14px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #7B3FE4;
            }
        """)
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn)
        
        layout.addStretch()
        
        # XÓA self.room_info ở đây
        # layout.addWidget(self.room_info)
        
        layout.addStretch()
        
        # Next button
        self.next_btn = QPushButton("Tiếp theo ➡️")
        self.next_btn.setMinimumHeight(50)
        self.next_btn.setEnabled(False)  # Disabled until room selected
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #6FCF97;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 14px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #5B2C8F;
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
        
    def select_floor(self, floor):
        """Chọn tầng"""
        self.current_floor = floor
        self.room_title.setText(f" Tầng {floor} ")
        self.update_room_display()
        
        # Reset selected room khi đổi tầng
        self.selected_room = None
        self.update_selection_display()
        
    def update_room_display(self):
        """Cập nhật hiển thị danh sách phòng theo tầng"""
        # Clear existing buttons
        for i in reversed(range(self.room_layout.count())): 
            self.room_layout.itemAt(i).widget().setParent(None)
            
        # Filter rooms by current floor
        floor_rooms = {k: v for k, v in self.room_data.items() 
                      if v["floor"] == self.current_floor}
        
        # Create room buttons
        self.room_buttons = QButtonGroup()
        row, col = 0, 0
        max_cols = 3
        
        for room_id, room_info in floor_rooms.items():
            btn = self.create_room_button(room_id, room_info)
            self.room_layout.addWidget(btn, row, col)
            self.room_buttons.addButton(btn)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
                
    def create_room_button(self, room_id, room_info):
        """Tạo button cho từng phòng"""
        btn = QPushButton()
        btn.setMinimumHeight(100)
        btn.setCheckable(True)

        # Icon theo loại phòng
        icons = {
            "room": "🏠",
            "vip": "⭐", 
            "public": "🏢"
        }
        icon = icons.get(room_info["type"], "🏠")

        # Button text: chỉ giữ icon và tên phòng
        btn.setText(f"{icon}\n{room_info['name']}")

        # Style theo loại phòng
        styles = {
            "room": "background-color: #5B2C8F;",
            "vip": "background-color: #F2994A;", 
            "public": "background-color: #6FCF97;"
        }
        base_style = styles.get(room_info["type"], "background-color: #5B2C8F;")
        btn.setStyleSheet(f"""
            QPushButton {{
                {base_style}
                border-radius: 18px;
                font-size: 18px;
                font-weight: bold;
                color: white;
                padding: 18px;
                margin: 8px;
            }}
            QPushButton:hover {{
                background-color: #7B3FE4;
            }}
            QPushButton:checked {{
                border: 4px solid #F2C94C;
                background-color: #F2C94C;
                color: #5B2C8F;
            }}
        """)

        btn.clicked.connect(lambda: self.select_room(room_id, room_info))
        return btn
        
    def select_room(self, room_id, room_info):
        """Chọn phòng"""
        self.selected_room = room_id
        self.selected_room_info = room_info
        self.update_selection_display()
        
        print(f"Đã chọn phòng: {room_info['name']} (ID: {room_id})")
        
    def update_selection_display(self):
        """Cập nhật hiển thị phòng được chọn"""
        if self.selected_room:
            info = self.selected_room_info
            self.selected_display.setText(f"✅ {info['name']}")
            # self.room_info.setText(f"Phòng được chọn: {info['name']} - Tầng {info['floor']} - SĐT: {info['phone']}")
            self.next_btn.setEnabled(True)
            self.selected_display.setStyleSheet("""
                background-color: #4CAF50; 
                color: white;
                border-radius: 10px; 
                padding: 5px 15px;
                font-weight: bold;
            """)
        else:
            self.selected_display.setText("Chưa chọn phòng")
            # self.room_info.setText("Chọn phòng để xem thông tin chi tiết")
            self.next_btn.setEnabled(False)
            self.selected_display.setStyleSheet("""
                background-color: rgba(255,255,255,0.3); 
                border-radius: 10px; 
                padding: 5px 15px;
            """)
            
    def go_back(self):
        """Quay lại màn hình trước"""
        print("Quay lại màn hình biểu cảm")
        self.back_screen.emit()
        
    def go_next(self):
        """Chuyển đến màn hình tiếp theo"""
        if self.selected_room:
            print(f"Chuyển đến màn hình chọn tủ - Phòng: {self.selected_room}")
            self.next_screen.emit(self.selected_room)
        
    def reset(self):
        """Reset về trạng thái ban đầu"""
        self.selected_room = None
        self.current_floor = 1
        self.floor_buttons.button(1).setChecked(True)
        self.select_floor(1)
        self.update_selection_display()
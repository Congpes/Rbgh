"""
Màn hình chọn đồ ăn
Hiển thị menu đồ ăn phù hợp với tủ đã chọn, với hình ảnh và thông tin chi tiết
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFrame, QGridLayout, QScrollArea, QButtonGroup,
                            QSpinBox, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor

class FoodSelectionScreen(QWidget):
    """Màn hình chọn đồ ăn"""
    
    # Signals
    next_screen = pyqtSignal(dict)  # Xác nhận toàn bộ đơn để sang chờ (nút sẽ ẩn)
    save_and_add_more = pyqtSignal(dict)  # Lưu đơn cho tủ hiện tại và quay lại chọn tủ
    back_screen = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.selected_foods = []  # Có thể chọn nhiều món
        self.cabinet_info = None
        self.cabinets_info = []  # hỗ trợ nhiều tủ
        self.active_cabinet_id = None
        self.food_data = self.load_food_data()
        self.filtered_foods = {}
        self.init_ui()
        
    def load_food_data(self):
        """Load danh sách đồ ăn (tạm thời hardcode, sau sẽ load từ JSON)"""
        return {
            "com_ga_nuong": {
                "name": "Cơm gà nướng",
                "price": 45000,
                "category": "main_dish",
                "image": "🍗",  # Sử dụng emoji tạm thời thay cho ảnh
                "description": "Cơm trắng thơm với gà nướng giòn tan, kèm rau củ tươi ngon",
                "cooking_time": 15,
                "available": True,
                "ingredients": ["gà", "cơm", "rau củ", "nước sốt"],
                "cabinet_type": ["left", "right"],
                "calories": 520,
                "rating": 4.5
            },
            "pho_bo": {
                "name": "Phở bò", 
                "price": 50000,
                "category": "noodle",
                "image": "🍜",
                "description": "Phở bò truyền thống với nước dùng đậm đà, thịt bò tươi ngon",
                "cooking_time": 10,
                "available": True,
                "ingredients": ["bánh phở", "thịt bò", "hành", "ngò", "nước dùng"],
                "cabinet_type": ["bottom"],
                "calories": 350,
                "rating": 4.8
            },
            "banh_mi": {
                "name": "Bánh mì thịt nướng",
                "price": 25000, 
                "category": "sandwich",
                "image": "🥖",
                "description": "Bánh mì Việt Nam giòn với thịt nướng thơm lừng và pate",
                "cooking_time": 5,
                "available": True,
                "ingredients": ["bánh mì", "thịt nướng", "pate", "rau thơm"],
                "cabinet_type": ["left", "right", "bottom"],
                "calories": 380,
                "rating": 4.3
            },
            "che_ba_mau": {
                "name": "Chè ba màu",
                "price": 20000,
                "category": "dessert", 
                "image": "🍧",
                "description": "Chè ba màu mát lạnh với đậu xanh, đậu đỏ và thạch dẻo",
                "cooking_time": 0,
                "available": True,
                "ingredients": ["đậu xanh", "đậu đỏ", "thạch", "nước cốt dừa"],
                "cabinet_type": ["bottom"],
                "calories": 180,
                "rating": 4.2
            },
            "nuoc_cam": {
                "name": "Nước cam tươi",
                "price": 15000,
                "category": "drink",
                "image": "🍊",
                "description": "Nước cam vắt tươi 100% tự nhiên, giàu vitamin C",
                "cooking_time": 2,
                "available": True, 
                "ingredients": ["cam tươi", "đá", "đường (tùy chọn)"],
                "cabinet_type": ["right", "bottom"],
                "calories": 85,
                "rating": 4.6
            },
            "ca_phe_sua": {
                "name": "Cà phê sữa đá",
                "price": 18000,
                "category": "drink",
                "image": "☕",
                "description": "Cà phê phin truyền thống với sữa đặc thơm ngon",
                "cooking_time": 5,
                "available": True,
                "ingredients": ["cà phê", "sữa đặc", "đá"],
                "cabinet_type": ["right"],
                "calories": 150,
                "rating": 4.4
            },
            "bun_bo_hue": {
                "name": "Bún bò Huế",
                "price": 55000,
                "category": "noodle",
                "image": "🍲",
                "description": "Bún bò Huế cay nồng đặc trưng miền Trung",
                "cooking_time": 12,
                "available": False,  # Hết hàng
                "ingredients": ["bún", "thịt bò", "chả", "tôm", "nước dùng cay"],
                "cabinet_type": ["bottom"],
                "calories": 420,
                "rating": 4.7
            }
        }
        
    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Main content
        content_layout = QHBoxLayout()
        
        # Category filter (bên trái)
        category_filter = self.create_category_filter()
        content_layout.addWidget(category_filter, 1)
        
        # Food grid (giữa)
        food_area = self.create_food_area()
        content_layout.addWidget(food_area, 3)
        
        # Order summary (bên phải)
        order_summary = self.create_order_summary()
        content_layout.addWidget(order_summary, 1)
        
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        layout.addWidget(content_widget, 1)
        
        # Footer
        footer = self.create_footer()
        layout.addWidget(footer)
        
        self.setLayout(layout)
        
    def create_header(self):
        """Tạo header"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("""
            QFrame {
                background-color: #E91E63;
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
        
        # Progress
        progress = QLabel("Bước 4/8")
        progress.setStyleSheet("background-color: rgba(255,255,255,0.2); border-radius: 10px; padding: 5px 10px;")
        layout.addWidget(progress)
        
        layout.addStretch()
        
        # Title
        title = QLabel("🍽️ Chọn Đồ Ăn")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Selected count
        self.selected_count = QLabel("0 món")
        self.selected_count.setStyleSheet("background-color: rgba(255,255,255,0.3); border-radius: 10px; padding: 5px 15px;")
        layout.addWidget(self.selected_count)
        
        frame.setLayout(layout)
        return frame
        
    def create_category_filter(self):
        """Tạo bộ lọc theo danh mục"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                margin: 5px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("📂 Danh Mục")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 10px; background-color: #2196F3; color: white; border-radius: 5px; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Category buttons
        self.category_buttons = QButtonGroup()
        categories = [
            ("all", "🍽️ Tất cả", "#607D8B"),
            ("main_dish", "🍗 Món chính", "#FF5722"),
            ("noodle", "🍜 Mì phở", "#9C27B0"),
            ("sandwich", "🥖 Bánh mì", "#795548"),
            ("dessert", "🍧 Tráng miệng", "#E91E63"),
            ("drink", "🥤 Đồ uống", "#00BCD4")
        ]
        
        for category_id, name, color in categories:
            btn = QPushButton(name)
            btn.setMinimumHeight(50)
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 8px;
                    margin: 2px;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
                QPushButton:checked {{
                    border: 3px solid #4CAF50;
                    background-color: #4CAF50;
                }}
            """)
            btn.clicked.connect(lambda checked, cat=category_id: self.filter_by_category(cat))
            self.category_buttons.addButton(btn)
            layout.addWidget(btn)
            
        # Select "all" by default
        self.category_buttons.buttons()[0].setChecked(True)
        self.current_category = "all"
        
        layout.addStretch()
        
        # Cabinet info
        self.cabinet_label = QLabel("Chưa chọn tủ")
        self.cabinet_label.setStyleSheet("""
            background-color: #f0f0f0; 
            border-radius: 5px; 
            padding: 10px; 
            font-size: 11px;
            border: 2px solid #ddd;
        """)
        self.cabinet_label.setWordWrap(True)
        layout.addWidget(self.cabinet_label)
        
        frame.setLayout(layout)
        return frame
        
    def create_food_area(self):
        """Tạo khu vực hiển thị đồ ăn"""
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
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Tìm kiếm:")
        search_label.setStyleSheet("font-weight: bold; padding: 5px;")
        search_layout.addWidget(search_label)
        
        # Có thể thêm QLineEdit cho tìm kiếm sau
        search_layout.addStretch()
        search_widget = QWidget()
        search_widget.setLayout(search_layout)
        layout.addWidget(search_widget)
        
        # Scrollable food grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.food_widget = QWidget()
        self.food_layout = QGridLayout(self.food_widget)
        self.food_layout.setSpacing(15)
        
        scroll.setWidget(self.food_widget)
        layout.addWidget(scroll, 1)
        
        # Update food display
        self.update_food_display()
        
        frame.setLayout(layout)
        return frame
        
    def create_order_summary(self):
        """Tạo tóm tắt đơn hàng"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                margin: 5px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🛒 Đơn Hàng")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Order list
        self.order_list = QTextEdit()
        self.order_list.setMaximumHeight(200)
        self.order_list.setReadOnly(True)
        self.order_list.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        self.order_list.setPlainText("Chưa có món nào được chọn...")
        layout.addWidget(self.order_list)
        
        # Total
        self.total_label = QLabel("Tổng cộng: 0 VNĐ")
        self.total_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.total_label.setAlignment(Qt.AlignCenter)
        self.total_label.setStyleSheet("""
            background-color: #FFC107; 
            color: #333; 
            border-radius: 8px; 
            padding: 10px;
            margin: 10px 0px;
        """)
        layout.addWidget(self.total_label)
        
        # Clear button
        clear_btn = QPushButton("🗑️ Xóa tất cả")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border-radius: 8px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        clear_btn.clicked.connect(self.clear_order)
        layout.addWidget(clear_btn)
        
        layout.addStretch()
        
        frame.setLayout(layout)
        return frame
        
    def create_food_item(self, food_id, food_info):
        """Tạo widget cho từng món ăn"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("""
            QFrame {
                background-color: #fafafa;
                border-radius: 15px;
                margin: 5px;
                padding: 15px;
                border: 2px solid #e0e0e0;
            }
            QFrame:hover {
                border: 2px solid #2196F3;
                background-color: #f0f8ff;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        
        # Food image (emoji)
        image_label = QLabel(food_info['image'])
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet("font-size: 60px; padding: 10px;")
        layout.addWidget(image_label)
        
        # Food name
        name_label = QLabel(food_info['name'])
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # Price
        price_label = QLabel(f"{food_info['price']:,} VNĐ")
        price_label.setAlignment(Qt.AlignCenter)
        price_label.setStyleSheet("""
            background-color: #FF5722; 
            color: white; 
            border-radius: 10px; 
            padding: 5px;
            font-weight: bold;
            font-size: 11px;
        """)
        layout.addWidget(price_label)
        
        # Rating and calories
        info_layout = QHBoxLayout()
        rating_label = QLabel(f"⭐ {food_info['rating']}")
        rating_label.setStyleSheet("font-size: 10px; color: #666;")
        info_layout.addWidget(rating_label)
        
        calories_label = QLabel(f"{food_info['calories']} cal")
        calories_label.setStyleSheet("font-size: 10px; color: #666;")
        info_layout.addWidget(calories_label)
        
        info_widget = QWidget()
        info_widget.setLayout(info_layout)
        layout.addWidget(info_widget)
        
        # Description (shortened)
        desc = food_info['description']
        if len(desc) > 60:
            desc = desc[:60] + "..."
        desc_label = QLabel(desc)
        desc_label.setStyleSheet("font-size: 10px; color: #666; font-style: italic;")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # Cooking time
        time_label = QLabel(f"⏱️ {food_info['cooking_time']} phút")
        time_label.setAlignment(Qt.AlignCenter)
        time_label.setStyleSheet("font-size: 10px; color: #666; padding: 5px;")
        layout.addWidget(time_label)
        
        # Quantity selector
        qty_layout = QHBoxLayout()
        qty_label = QLabel("Số lượng:")
        qty_label.setStyleSheet("font-size: 10px; font-weight: bold;")
        qty_layout.addWidget(qty_label)
        
        qty_spinbox = QSpinBox()
        qty_spinbox.setMinimum(0)
        qty_spinbox.setMaximum(10)
        qty_spinbox.setValue(0)
        qty_spinbox.setStyleSheet("""
            QSpinBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 2px;
                font-size: 10px;
            }
        """)
        qty_spinbox.valueChanged.connect(lambda value: self.update_food_quantity(food_id, food_info, value))
        qty_layout.addWidget(qty_spinbox)
        
        qty_widget = QWidget()
        qty_widget.setLayout(qty_layout)
        layout.addWidget(qty_widget)
        
        # Availability status
        if not food_info['available']:
            # Overlay for unavailable items
            frame.setStyleSheet("""
                QFrame {
                    background-color: #f0f0f0;
                    border-radius: 15px;
                    margin: 5px;
                    padding: 15px;
                    border: 2px solid #ccc;
                    opacity: 0.5;
                }
            """)
            
            unavailable_label = QLabel("❌ Hết hàng")
            unavailable_label.setAlignment(Qt.AlignCenter)
            unavailable_label.setStyleSheet("""
                background-color: #F44336; 
                color: white; 
                border-radius: 8px; 
                padding: 5px;
                font-weight: bold;
                font-size: 10px;
            """)
            layout.addWidget(unavailable_label)
            
            qty_spinbox.setEnabled(False)
        
        frame.setLayout(layout)
        return frame
        
    def create_footer(self):
        """Tạo footer"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 10px;
                margin: 10px;
                padding: 15px;
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
        
        # Order info
        self.order_info = QLabel("Chọn món ăn để xem tổng đơn hàng")
        self.order_info.setStyleSheet("color: #666; font-style: italic; padding: 15px;")
        layout.addWidget(self.order_info)
        
        layout.addStretch()
        
        # Save and add more button
        self.save_more_btn = QPushButton("💾 Lưu tủ này & chọn thêm")
        self.save_more_btn.setMinimumHeight(50)
        self.save_more_btn.setEnabled(False)
        self.save_more_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.save_more_btn.clicked.connect(self.save_current_cabinet_order)
        layout.addWidget(self.save_more_btn)
        
        # BỎ nút qua chờ ở Food: auto quay về Cabinet hoặc auto sang chờ khi đủ 3 tủ
        
        frame.setLayout(layout)
        return frame
        
    def filter_by_category(self, category):
        """Lọc đồ ăn theo danh mục"""
        self.current_category = category
        self.update_food_display()
        print(f"Lọc theo danh mục: {category}")
        
    def update_food_display(self):
        """Cập nhật hiển thị danh sách đồ ăn"""
        # Clear existing items
        for i in reversed(range(self.food_layout.count())):
            self.food_layout.itemAt(i).widget().setParent(None)
            
        # Filter foods
        if self.current_category == "all":
            self.filtered_foods = self.food_data.copy()
        else:
            self.filtered_foods = {k: v for k, v in self.food_data.items() 
                                 if v["category"] == self.current_category}
            
        # Further filter by cabinet compatibility if cabinet is selected
        cabinet_ids = []
        if self.cabinets_info:
            cabinet_ids = [c.get("id") for c in self.cabinets_info if c.get("id")]
        elif self.cabinet_info:
            # backward compat: single cabinet
            cid = self.cabinet_info.get("id")
            cabinet_ids = [cid] if cid else []

        if cabinet_ids:
            self.filtered_foods = {k: v for k, v in self.filtered_foods.items()
                                   if any(cid in v.get("cabinet_type", []) for cid in cabinet_ids)}
        
        # Create food items
        row, col = 0, 0
        max_cols = 2
        
        for food_id, food_info in self.filtered_foods.items():
            food_widget = self.create_food_item(food_id, food_info)
            self.food_layout.addWidget(food_widget, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
                
        print(f"Hiển thị {len(self.filtered_foods)} món ăn")
        
    def update_food_quantity(self, food_id, food_info, quantity):
        """Cập nhật số lượng món ăn"""
        # Remove existing entry
        self.selected_foods = [item for item in self.selected_foods if item['id'] != food_id]
        
        # Add new entry if quantity > 0
        if quantity > 0:
            self.selected_foods.append({
                'id': food_id,
                'info': food_info,
                'quantity': quantity,
                'total_price': food_info['price'] * quantity
            })
            
        self.update_order_summary()
        
    def update_order_summary(self):
        """Cập nhật tóm tắt đơn hàng"""
        if not self.selected_foods:
            self.order_list.setPlainText("Chưa có món nào được chọn...")
            self.total_label.setText("Tổng cộng: 0 VNĐ")
            self.selected_count.setText("0 món")
            self.order_info.setText("Chọn món ăn để xem tổng đơn hàng")
            self.save_more_btn.setEnabled(False)
            return
            
        # Build order text
        order_text = ""
        total_amount = 0
        total_items = 0
        
        for item in self.selected_foods:
            name = item['info']['name']
            qty = item['quantity']
            price = item['info']['price']
            total_price = item['total_price']
            
            order_text += f"• {name}\n"
            order_text += f"  {qty} x {price:,} = {total_price:,} VNĐ\n\n"
            
            total_amount += total_price
            total_items += qty
            
        self.order_list.setPlainText(order_text)
        self.total_label.setText(f"Tổng cộng: {total_amount:,} VNĐ")
        self.selected_count.setText(f"{total_items} món")
        self.order_info.setText(f"{len(self.selected_foods)} loại món, {total_items} món tổng cộng")
        self.save_more_btn.setEnabled(True)
        
    def clear_order(self):
        """Xóa tất cả đơn hàng"""
        self.selected_foods = []
        self.update_order_summary()
        
        # Reset all spinboxes
        self.update_food_display()
        print("Đã xóa tất cả đơn hàng")
        
    def set_cabinet_info(self, cabinet_id, cabinet_info):
        """Set thông tin tủ từ màn hình trước"""
        self.cabinet_info = {"id": cabinet_id, "info": cabinet_info}
        
        suitable_items = ", ".join(cabinet_info['suitable_for'])
        self.cabinet_label.setText(f"""
            Tủ: {cabinet_info['name']}
            Phù hợp: {suitable_items.replace('_', ' ')}
        """)
        
        # Update food display to show only compatible foods
        self.update_food_display()
        print(f"Food selection for cabinet: {cabinet_info.get('name', cabinet_id)}")

    def set_cabinets_info(self, cabinets_list):
        """Nhận danh sách nhiều tủ đã chọn"""
        self.cabinets_info = cabinets_list or []
        if not self.cabinets_info:
            self.cabinet_label.setText("Chưa chọn tủ")
        else:
            names = ", ".join([c.get("info", {}).get("name", c.get("id", "?")) for c in self.cabinets_info])
            self.cabinet_label.setText(f"Đang dùng các tủ: {names}")
        self.update_food_display()

    def set_active_cabinet(self, cabinet_id: str):
        """Đặt tủ đang thao tác để lưu đơn theo từng tủ"""
        self.active_cabinet_id = cabinet_id
        
    def go_back(self):
        """Quay lại màn hình trước"""
        print("Quay lại màn hình chọn tủ")
        self.back_screen.emit()
        
    def go_next(self):
        """Chuyển đến màn hình tiếp theo"""
        if self.selected_foods:
            order_data = {
                'foods': self.selected_foods,
                'cabinets': self.cabinets_info if self.cabinets_info else ([self.cabinet_info] if self.cabinet_info else []),
                'total_amount': sum(item['total_price'] for item in self.selected_foods),
                'total_items': sum(item['quantity'] for item in self.selected_foods)
            }
            print(f"Xác nhận đơn hàng: {len(self.selected_foods)} loại món")
            self.next_screen.emit(order_data)

    def save_current_cabinet_order(self):
        """Lưu đơn hàng cho tủ đang thao tác và quay lại chọn tủ khác"""
        if not self.selected_foods or not self.active_cabinet_id:
            return
        data = {
            'cabinet_id': self.active_cabinet_id,
            'foods': self.selected_foods,
            'total_amount': sum(item['total_price'] for item in self.selected_foods),
            'total_items': sum(item['quantity'] for item in self.selected_foods)
        }
        print(f"Lưu đơn cho tủ {self.active_cabinet_id}: {len(self.selected_foods)} loại món")
        self.save_and_add_more.emit(data)
            
    def reset(self):
        """Reset về trạng thái ban đầu"""
        self.selected_foods = []
        self.current_category = "all"
        self.cabinet_info = None
        self.category_buttons.buttons()[0].setChecked(True)
        self.update_order_summary()
        self.update_food_display()
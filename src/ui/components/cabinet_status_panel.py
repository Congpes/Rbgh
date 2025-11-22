"""
Component bảng trạng thái 3 tủ - giống hệt setup_delivery
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class CabinetStatusPanel(QWidget):
    """Panel hiển thị trạng thái 3 tủ - giống hệt setup_delivery"""
    
    # Signal
    cabinet_clicked = pyqtSignal(str)  # cabinet_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cabinets = {}
        self.current_room = None
        self.init_ui()
        
    def init_ui(self):
        """Khởi tạo giao diện - giống hệt setup_delivery"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tạo 3 tủ theo layout 2 trên, 1 dưới - giảm khoảng cách
        top_row = QHBoxLayout()
        top_row.setSpacing(20)
        
        # Tủ trái - giống setup_delivery
        self.cabinet_left = self._create_cabinet_tile("left")
        top_row.addWidget(self.cabinet_left)
        
        # Tủ phải - giống setup_delivery  
        self.cabinet_right = self._create_cabinet_tile("right")
        top_row.addWidget(self.cabinet_right)
        
        layout.addLayout(top_row)
        
        # Tủ dưới (rộng hơn) - giảm khoảng cách với tủ trên
        self.cabinet_bottom = self._create_cabinet_tile("bottom", wide=True)
        layout.addWidget(self.cabinet_bottom)
        
        # Giảm spacing giữa các tủ - giảm thêm nữa
        layout.setSpacing(5)  # Giảm từ 10 xuống 5
        
        # Lưu vào dict để dễ quản lý
        self.cabinets = {
            "left": self.cabinet_left,
            "right": self.cabinet_right,
            "bottom": self.cabinet_bottom
        }
        
        self.setLayout(layout)
        
    def _cabinet_tile_style(self, active: bool, picked: bool = False) -> str:
        """Style cho tủ.
        - active (có đồ cho phòng): nền #31C7E9
        - picked (đã lấy đồ): nền cam #FD9D2F
        """
        if picked:
            base = "background:#FD9D2F; border-radius:14px; border:3px solid #F07F00;"
        elif active:
            base = "background:#31C7E9; border-radius:14px; border:3px solid #1E8FA8;"
        else:
            base = "background:#6257CA; border-radius:14px; border:none;"
        return (
            f"QFrame {{ {base} }} "
            "QLabel { color:white; font-weight:bold; background:transparent; border:none; }"
        )

    def _create_cabinet_tile(self, cid: str, wide: bool = False) -> QWidget:
        """Tạo tủ - nhỏ lại vừa đủ như setup"""
        frame = QFrame()
        frame.setObjectName(f"cabinet_{cid}")
        frame.setStyleSheet(self._cabinet_tile_style(False))
        frame.setMinimumHeight(80 if not wide else 100)  # Nhỏ lại
        frame.setMaximumHeight(80 if not wide else 100)  # Giới hạn chiều cao

        v = QVBoxLayout()
        v.setContentsMargins(8, 8, 8, 8)  # Margin nhỏ hơn
        # Chỉ có 1 label ở giữa - xóa số 1,2,3 và "tap to open"
        label = QLabel("No delivery")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 16, QFont.Bold))  # Chữ to

        v.addWidget(label)
        frame.setLayout(v)

        def on_click():
            self.cabinet_clicked.emit(cid)

        frame.mousePressEvent = lambda e: on_click()
        return frame
        
    def update_for_room(self, room_number, delivery_cabinets, picked_cabinets=None):
        """Cập nhật trạng thái tủ cho phòng hiện tại"""
        self.current_room = room_number
        picked_cabinets = picked_cabinets or []
        
        # Reset tất cả tủ về "No delivery"
        for cid, cabinet in self.cabinets.items():
            cabinet.setStyleSheet(self._cabinet_tile_style(False))
            # Cập nhật text thành "No delivery"
            label = cabinet.layout().itemAt(0).widget()
            label.setText("No delivery")
            
        # Cập nhật tủ có đồ cho phòng này - màu #31C7E9 + số phòng
        for cabinet_id in delivery_cabinets:
            if cabinet_id in self.cabinets:
                cabinet = self.cabinets[cabinet_id]
                cabinet.setStyleSheet(self._cabinet_tile_style(True))
                # Cập nhật text thành số phòng
                label = cabinet.layout().itemAt(0).widget()
                label.setText(str(room_number))

        # Đánh dấu tủ đã lấy đồ (Delivery picked up) – nền cam
        for cabinet_id in picked_cabinets:
            if cabinet_id in self.cabinets:
                cabinet = self.cabinets[cabinet_id]
                cabinet.setStyleSheet(self._cabinet_tile_style(False, picked=True))
                label = cabinet.layout().itemAt(0).widget()
                label.setText("Delivery picked up")
                
    def get_delivery_cabinet(self):
        """Lấy tủ đang chứa đồ cho phòng hiện tại"""
        for cabinet in self.cabinets.values():
            if cabinet.styleSheet().find("border:3px solid white") != -1:
                return cabinet
        return None
"""
Setup Delivery Screen - Hợp nhất cabinet_selection + room_selection theo mock
Màu nền: #1C1492, các ô/button: #6257CA

Chức năng: 
- 3 tủ: 1,2,3 (trái, phải, dưới). Tap to open → trạng thái open
- Chọn phòng ở lưới phải. Khi đã chọn 1 tủ (open) + 1 phòng → enable Close door
- Close door: gán phòng vào tủ, tủ về trạng thái closed, label đổi thành số phòng
- Click lại tủ đã gán → hiện Delete để xóa gán; cần nhấn Close door để đóng lại
- Go deliver: enable khi có ≥1 tủ đã gán phòng
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QGridLayout, QScrollArea, QButtonGroup, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class SetupDeliveryScreen(QWidget):
    """Màn hình hợp nhất setup delivery"""

    back_screen = pyqtSignal()
    go_deliver = pyqtSignal(dict)  # payload: draft state

    def __init__(self, rooms_data: dict = None):
        super().__init__()
        self.setObjectName("setupDelivery")
        self.rooms_data = rooms_data or {}

        # State
        self.cabinets = {
            "left": {"id": "left", "label": "1", "status": "closed", "assignedRoomId": None, "description": ""},
            "right": {"id": "right", "label": "2", "status": "closed", "assignedRoomId": None, "description": ""},
            "bottom": {"id": "bottom", "label": "3", "status": "closed", "assignedRoomId": None, "description": ""},
        }
        self.active_cabinet_id = None
        self.selected_room_id = None

        self.current_floor = 1
        self.init_ui()

    # ---------- UI ----------
    def init_ui(self):
        # Nền giống home_screen: dùng QPalette để đảm bảo áp dụng
        from PyQt5.QtGui import QPalette, QColor
        pal = QPalette()
        pal.setColor(QPalette.Window, QColor(28, 20, 146))  # #1C1492
        self.setPalette(pal)
        self.setAutoFillBackground(True)
        self.setStyleSheet("""
            QLabel, QPushButton { font-family: Arial; }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        header = self._create_header()
        main_layout.addWidget(header)

        body = QHBoxLayout()
        body.setSpacing(24)

        left_pane = self._create_left_pane()
        right_pane = self._create_right_pane()

        body.addWidget(left_pane, 1)
        body.addWidget(right_pane, 1)

        main_layout.addLayout(body, 1)

        footer = self._create_footer()
        main_layout.addWidget(footer)

        self.setLayout(main_layout)

    def _create_header(self) -> QWidget:
        frame = QFrame()
        layout = QHBoxLayout()
        title = QLabel("Delivery")
        title.setStyleSheet("color: white; font-weight: bold;")
        title.setFont(QFont("Arial", 18, QFont.Bold))

        back = QPushButton("←")
        back.setFixedSize(40, 40)
        back.setStyleSheet("""
            QPushButton { background-color: #6257CA; color: white; border-radius: 20px; border: 2px solid white; }
            QPushButton:hover { background-color: #6f66d3; }
        """)
        back.clicked.connect(self.back_screen.emit)

        layout.addWidget(back, 0, Qt.AlignLeft)
        layout.addWidget(title, 0, Qt.AlignLeft)
        layout.addStretch()
        frame.setLayout(layout)
        return frame

    def _create_left_pane(self) -> QWidget:
        frame = QFrame()
        frame.setStyleSheet("QFrame { background: transparent; }")
        layout = QVBoxLayout()
        layout.setSpacing(16)

        # Group container cho toàn bộ khu tủ (gộp 1 khung)
        group = QFrame()
        group.setStyleSheet("""
            QFrame { background: rgba(255,255,255,0.08); border: none; border-radius: 12px; }
        """)
        g_lay = QVBoxLayout()
        g_lay.setContentsMargins(12, 12, 12, 12)
        g_lay.setSpacing(12)
        # Row 1: 1 & 2
        row1 = QHBoxLayout()
        row1.setSpacing(12)
        self.tile_left = self._create_cabinet_tile("left")
        self.tile_right = self._create_cabinet_tile("right")
        row1.addWidget(self.tile_left, 1)
        row1.addWidget(self.tile_right, 1)
        g_lay.addLayout(row1)
        # Row 2: 3 full width
        self.tile_bottom = self._create_cabinet_tile("bottom", wide=True)
        g_lay.addWidget(self.tile_bottom)
        group.setLayout(g_lay)
        layout.addWidget(group)

        # Description box
        self.desc_box = QTextEdit()
        self.desc_box.setPlaceholderText("Enter the destination (optional).")
        self.desc_box.setStyleSheet("""
            QTextEdit { background:#0d0d4d; color:#fff; border-radius: 10px; padding: 12px; }
        """)
        layout.addWidget(self.desc_box)

        # Close door button
        self.close_btn = QPushButton("Close the door")
        self.close_btn.setEnabled(False)
        self.close_btn.setStyleSheet("""
            QPushButton { background:#6257CA; color:white; border-radius:24px; padding:12px 24px; font-weight:600; }
            QPushButton:disabled { background:#49418f; color:#C9C9E9; }
        """)
        self.close_btn.clicked.connect(self.on_close_door)
        layout.addWidget(self.close_btn, 0, Qt.AlignLeft)

        frame.setLayout(layout)
        return frame

    def _cabinet_tile_style(self, active: bool, assigned_text: str = None) -> str:
        base = "background:#6257CA; border-radius:14px;"
        border = "border:3px solid white;" if active else "border:none;"
        return (
            f"QFrame {{ {base}{border} }} "
            "QLabel { color:white; font-weight:bold; background:transparent; border:none; }"
        )

    def _create_cabinet_tile(self, cid: str, wide: bool = False) -> QWidget:
        frame = QFrame()
        frame.setObjectName(f"cabinet_{cid}")
        frame.setStyleSheet(self._cabinet_tile_style(False))
        frame.setMinimumHeight(96 if not wide else 120)

        v = QVBoxLayout()
        v.setContentsMargins(12, 12, 12, 12)
        top = QLabel("%s" % ("1" if cid == "left" else "2" if cid == "right" else "3"))
        top.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        label = QLabel("Tap to open")
        label.setAlignment(Qt.AlignCenter)

        v.addWidget(top)
        v.addStretch()
        v.addWidget(label)
        frame.setLayout(v)

        def on_click():
            self.on_cabinet_clicked(cid, label)

        frame.mousePressEvent = lambda e: on_click()  # simple tile click
        frame._label_ref = label  # keep for update text
        return frame

    def _create_right_pane(self) -> QWidget:
        frame = QFrame()
        # Bỏ nền trắng, dùng cùng màu nền tổng #1C1492 (hoặc trong suốt)
        frame.setStyleSheet("QFrame { background: #1C1492; border: none; }")
        v = QVBoxLayout()
        v.setContentsMargins(16, 16, 16, 16)
        # Floor selector buttons 1..4
        self.floor_btn_group = QButtonGroup()
        floors_row = QHBoxLayout()
        floors_row.setSpacing(12)
        for n in [1, 2, 3, 4]:
            b = QPushButton(str(n))
            b.setCheckable(True)
            if n == self.current_floor:
                b.setChecked(True)
            b.setStyleSheet("""
                QPushButton { background:#6257CA; color:#fff; border-radius:10px; min-width:44px; min-height:28px; }
                QPushButton:checked { border:2px solid #fff; }
            """)
            b.clicked.connect(lambda checked, f=n: self._on_floor_selected(f))
            self.floor_btn_group.addButton(b, n)
            floors_row.addWidget(b, 1, Qt.AlignCenter)
        v.addLayout(floors_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        # Đồng bộ nền cuộn với nền tổng 1C1492 (tránh panel trắng)
        scroll.setStyleSheet("""
            QScrollArea { background: #1C1492; border: none; }
            QScrollArea > QWidget { background: #1C1492; }
            QScrollArea > QWidget > QWidget { background: #1C1492; }
        """)
        inner = QWidget()
        inner.setStyleSheet("background: #1C1492;")
        grid = QGridLayout(inner)
        grid.setSpacing(18)
        grid.setContentsMargins(8, 12, 8, 12)

        # Build rooms for current floor
        room_ids = self._get_rooms_for_floor(self.current_floor)
        self.room_buttons = {}
        # Group để đảm bảo chỉ chọn 1 phòng
        self.room_btn_group = QButtonGroup()
        self.room_btn_group.setExclusive(True)
        r, c = 0, 0
        for rid in room_ids:
            btn = QPushButton(rid)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton { background:#E5E5E5; color:#000; border-radius:10px; min-width:96px; min-height:52px; }
                QPushButton:checked { background:#6257CA; color:#fff; border:2px solid #fff; }
            """)
            btn.clicked.connect(lambda checked, rr=rid: self.on_room_selected(rr))
            grid.addWidget(btn, r, c)
            self.room_buttons[rid] = btn
            self.room_btn_group.addButton(btn)
            c += 1
            if c >= 4:
                c = 0
                r += 1

        inner.setLayout(grid)
        scroll.setWidget(inner)
        v.addWidget(scroll, 1)
        frame.setLayout(v)
        return frame

    def _create_footer(self) -> QWidget:
        frame = QFrame()
        h = QHBoxLayout()
        h.addStretch()
        self.go_btn = QPushButton("Go deliver")
        self.go_btn.setEnabled(False)
        self.go_btn.setStyleSheet("""
            QPushButton { background:#6257CA; color:white; border-radius:24px; padding:12px 28px; font-weight:600; }
            QPushButton:disabled { background:#49418f; color:#C9C9E9; }
        """)
        self.go_btn.clicked.connect(self.on_go_deliver)
        h.addWidget(self.go_btn)
        frame.setLayout(h)
        return frame

    # ---------- Interactions ----------
    def on_cabinet_clicked(self, cid: str, label_widget: QLabel):
        cab = self.cabinets[cid]
        if cab["assignedRoomId"]:
            # Ask delete
            ans = QMessageBox.question(self, "Delete", "Xóa phòng đã gán cho tủ này?",
                                       QMessageBox.Yes | QMessageBox.No)
            if ans == QMessageBox.Yes:
                cab["assignedRoomId"] = None
                cab["status"] = "open"  # mở ra để thao tác lại
                self._update_cabinet_tile(cid)
                self._update_buttons_state()
            return

        # Chỉ cho phép 1 tủ mở: đóng các tủ khác nếu đang mở và chưa gán
        for other_id, other in self.cabinets.items():
            if other_id != cid and other.get("status") == "open" and not other.get("assignedRoomId"):
                other["status"] = "closed"
                self._update_cabinet_tile(other_id)

        # Open cabinet hiện tại
        cab["status"] = "open"
        self.active_cabinet_id = cid
        self._update_cabinet_tile(cid)
        self._update_buttons_state()

    def on_room_selected(self, room_id: str):
        self.selected_room_id = room_id
        self._update_buttons_state()

    def _on_floor_selected(self, floor: int):
        self.current_floor = floor
        # rebuild right pane (only grid) — simplest: recreate whole right pane
        parent_layout: QHBoxLayout = self.layout().itemAt(1)
        # itemAt(1) is body HBox: left, right
        try:
            body = parent_layout
            right = body.itemAt(1).widget()
            if right:
                right.setParent(None)
            body.addWidget(self._create_right_pane(), 1)
        except Exception:
            pass

    def on_close_door(self):
        if not (self.active_cabinet_id and self.selected_room_id):
            return
        cab = self.cabinets[self.active_cabinet_id]
        # Lưu mô tả hiện tại vào tủ đang thao tác
        cab["description"] = self.desc_box.toPlainText().strip()
        cab["assignedRoomId"] = self.selected_room_id
        cab["status"] = "closed"
        # Update label text on tile
        self._update_cabinet_tile(self.active_cabinet_id)
        # Lưu xuống file session
        self._save_session()
        # Reset selection for next cabinet
        self.active_cabinet_id = None
        self.selected_room_id = None
        for btn in self.room_buttons.values():
            btn.setChecked(False)
        # Xóa mô tả cũ trên UI sau khi lưu
        self.desc_box.clear()
        self._update_buttons_state()

    def on_go_deliver(self):
        draft = {
            "cabinets": self.cabinets,
            "note": self.desc_box.toPlainText().strip(),
        }
        self.go_deliver.emit(draft)

    # ---------- Helpers ----------
    def _update_cabinet_tile(self, cid: str):
        frame: QFrame = getattr(self, f"tile_{'left' if cid=='left' else 'right' if cid=='right' else 'bottom'}")
        cab = self.cabinets[cid]
        active = (self.active_cabinet_id == cid or cab["status"] == "open") and not cab.get("assignedRoomId")
        frame.setStyleSheet(self._cabinet_tile_style(active))
        # update label text
        label: QLabel = frame._label_ref
        label.setText(cab["assignedRoomId"] or "Tap to open")

    def _update_buttons_state(self):
        # Close door enabled when an active cabinet and a room chosen
        can_close = bool(self.active_cabinet_id and self.selected_room_id)
        self.close_btn.setEnabled(can_close)
        # Go deliver enabled when any cabinet assigned
        any_assigned = any(c["assignedRoomId"] for c in self.cabinets.values())
        self.go_btn.setEnabled(any_assigned)

    def _get_rooms_for_floor(self, floor: int):
        """Trả danh sách phòng theo tầng dựa hoàn toàn vào rooms.json (self.rooms_data)."""
        import re
        ids = []
        for rid, info in (self.rooms_data or {}).items():
            try:
                if int(info.get("floor", 0)) == floor:
                    ids.append(rid)
            except Exception:
                continue
        # Sắp xếp: theo số ở cuối (nếu có), rồi theo tên
        def sort_key(rid: str):
            m = re.search(r"(\d+)$", rid)
            return (int(m.group(1)) if m else 0, rid)
        ids.sort(key=sort_key)
        return ids

    # ---------- Persistence ----------
    def _save_session(self):
        import os, json
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        data_dir = os.path.join(root, "data")
        os.makedirs(data_dir, exist_ok=True)
        path = os.path.join(data_dir, "session.json")
        payload = {
            "cabinets": self.cabinets,
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Save session failed:", e)

    # Public API
    def reset(self):
        for cab in self.cabinets.values():
            cab["status"] = "closed"
            cab["assignedRoomId"] = None
            cab["description"] = ""
        self.active_cabinet_id = None
        self.selected_room_id = None
        self.desc_box.clear()
        self._update_cabinet_tile("left")
        self._update_cabinet_tile("right")
        self._update_cabinet_tile("bottom")
        self._update_buttons_state()



import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from src.core.delivery_manager import DeliveryManager

# Import các màn hình
from src.ui.home_screen import HomeScreen

class MainWindow(QMainWindow):
    """Cửa sổ chính của ứng dụng"""
    
    def __init__(self):
        super().__init__()
        # Trạng thái
        self.selected_cabinets = []  # Danh sách tủ đã xác nhận (mỗi phần tử: {id, info, foods?, total?}); tối đa 3 tủ/phòng
        self.current_room = None
        self.current_cabinet = None
        self.current_order = None
        # Delivery Manager
        self.delivery_manager = DeliveryManager()
        self.init_ui()
        self.init_screens()
        self.setup_navigation()
        
    def init_ui(self):
        """Khởi tạo giao diện chính"""
        self.setWindowTitle("Robot Giao Đồ Ăn - Food Delivery Robot")
        self.setGeometry(100, 100, 1024, 768)  # Kích thước màn hình robot
        
        font = QFont("Arial", 12)
        self.setFont(font)
        
        # Tạo stack widget để chứa các màn hình
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Style cho ứng dụng
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
        """)
        
    def init_screens(self):
        """Khởi tạo tất cả các màn hình"""
        # Import các màn hình
        from src.ui.emotion_screen import EmotionScreen
        from src.ui.setup_delivery import SetupDeliveryScreen
        from src.ui.waiting_screen import WaitingScreen
        from src.ui.pickup_screen import PickupScreen
        from src.ui.confirmation_screen import ConfirmationScreen
        from src.ui.comeback import ComebackScreen

        # Khởi tạo các màn hình
        self.home_screen = HomeScreen()
        self.emotion_screen = EmotionScreen()
        # Màn hình hợp nhất setup delivery thay thế room_selection và cabinet_selection
        self.setup_delivery_screen = SetupDeliveryScreen(rooms_data=self.delivery_manager.rooms_data)
        self.waiting_screen = WaitingScreen()
        self.pickup_screen = PickupScreen()
        self.confirmation_screen = ConfirmationScreen()
        self.comeback_screen = ComebackScreen()

        # Thêm vào stack
        self.stacked_widget.addWidget(self.emotion_screen)           # index 0
        self.stacked_widget.addWidget(self.home_screen)              # index 1
        self.stacked_widget.addWidget(self.setup_delivery_screen)    # index 2
        self.stacked_widget.addWidget(self.waiting_screen)           # index 3
        self.stacked_widget.addWidget(self.pickup_screen)            # index 4
        self.stacked_widget.addWidget(self.confirmation_screen)      # index 5
        self.stacked_widget.addWidget(self.comeback_screen)          # index 6

        # Bắt đầu với màn hình emotion
        self.stacked_widget.setCurrentIndex(0)
    
    def on_app_selected(self, app_id):
        """Xử lý khi chọn ứng dụng từ home screen"""
        if app_id == "delivery":
            # Chuyển đến màn hình hợp nhất setup delivery
            self.show_setup_delivery()
        elif app_id == "cabinet":
            # Chuyển đến setup delivery (thay thế cabinet selection)
            self.show_setup_delivery()
        elif app_id == "settings":
            print("Mở cài đặt (chưa implement)")
        elif app_id == "help":
            print("Mở trợ giúp (chưa implement)")
        elif app_id == "about":
            print("Mở giới thiệu (chưa implement)")
        else:
            print(f"Ứng dụng {app_id} chưa được hỗ trợ")
        
    def setup_navigation(self):
        """Thiết lập điều hướng giữa các màn hình"""
        # Home → Emotion
        self.home_screen.app_selected.connect(self.on_app_selected)
        self.home_screen.back_screen.connect(self.show_emotion_screen)
        
        # Emotion → Home
        self.emotion_screen.next_screen.connect(self.show_home_screen)
        
        # SetupDelivery navigation (thay thế room_selection và cabinet_selection)
        self.setup_delivery_screen.back_screen.connect(self.show_home_screen)
        self.setup_delivery_screen.go_deliver.connect(self.on_setup_go_deliver)
        
        # Waiting → Confirmation
        self.waiting_screen.next_screen.connect(self.show_confirmation_screen)
        self.waiting_screen.cancel_screen.connect(self.show_setup_delivery)

        # Confirmation ↔ Active cabinet (pickup_screen dùng làm màn active)
        self.confirmation_screen.open_cabinet.connect(self.show_active_open)
        self.confirmation_screen.close_cabinet.connect(self.show_active_close)
        self.pickup_screen.opened.connect(self.on_active_opened)
        self.pickup_screen.closed.connect(self.on_active_closed)

    def show_setup_delivery(self):
        """Hiển thị màn hình setup delivery hợp nhất"""
        # Reset màn khi vào lại
        try:
            self.setup_delivery_screen.reset()
        except Exception:
            pass
        self.stacked_widget.setCurrentIndex(2)

    def on_setup_go_deliver(self, draft: dict):
        """Nhận draft từ setup_delivery và chuyển sang màn chờ (waiting)"""
        print("Go deliver with draft:", draft)
        
        # Thu thập các tủ đã gán phòng
        assigned_cabinets = []
        for cabinet_id, cabinet_info in draft.get('cabinets', {}).items():
            room_assigned = cabinet_info.get('assignedRoomId')
            if room_assigned:
                assigned_cabinets.append({
                    "id": cabinet_id,
                    "name": cabinet_info.get('name', ''),
                    "position": cabinet_info.get('position', ''),
                    "status": "locked",
                    "is_open": False,
                    "items_confirmed": False,
                    "assigned_room_id": room_assigned,
                    "description": cabinet_info.get('description', ''),
                    "items_count": 0
                })

        # Nhóm theo phòng: nếu cùng phòng thì gộp nhiều tủ vào 1 delivery
        if assigned_cabinets:
            room_to_cabinets = {}
            for cab in assigned_cabinets:
                rid = cab.get('assigned_room_id')
                room_to_cabinets.setdefault(rid, []).append(cab)

            for rid, cabs in room_to_cabinets.items():
                self.delivery_manager.add_delivery(room_id=rid, cabinets=cabs)

            # Lưu session với phòng đầu tiên
            first_room_id = list(room_to_cabinets.keys())[0]
            room_info = self.delivery_manager.rooms_data.get(first_room_id, {})
            try:
                from src.utils import storage
                session_data = {
                    'room': {
                        "id": first_room_id,
                        "info": room_info
                    },
                    'cabinets': room_to_cabinets[first_room_id]
                }
                storage.save_session(storage.default_session_path(), session_data)
            except Exception as _:
                pass
        
        self.show_waiting_screen()
        
        # Confirmation → Pickup (chỉ khi nhận đồ) hoặc Next room (khi hủy/không phản hồi)
        self.confirmation_screen.restart_screen.connect(self.reset_to_emotion)
        self.confirmation_screen.home_screen.connect(self.reset_to_emotion)
        self.confirmation_screen.confirmed.connect(self.show_pickup_screen)  # Chỉ khi nhận đồ
        self.confirmation_screen.cancelled.connect(self.on_confirmation_cancelled)  # Xử lý hủy đơn
        self.confirmation_screen.items_picked.connect(self.on_items_picked)
        self.confirmation_screen.phone_call_started.connect(self.on_confirmation_phone_call_started)
        self.confirmation_screen.phone_call_stopped.connect(self.on_confirmation_phone_call_stopped)
        self.pickup_screen.report_issue.connect(self.handle_issue_report)
        self.comeback_screen.done.connect(self.reset_to_emotion)

        # Pickup screen connections
        self.pickup_screen.done.connect(self.on_pickup_completed)  # Xử lý khi lấy xong
        self.pickup_screen.report_issue.connect(self.handle_issue_report)
        self.pickup_screen.cancel_task.connect(self.on_cancel_task)

    def show_emotion_screen(self):
        """Hiển thị màn hình biểu cảm"""
        self.stacked_widget.setCurrentIndex(0)
        
    def show_home_screen(self):
        """Hiển thị màn hình home"""
        self.stacked_widget.setCurrentIndex(1)
        
        
    def show_waiting_screen(self):
        """Hiển thị màn hình chờ"""
        # Lấy thông tin phòng hiện tại từ delivery manager
        current_delivery = self.delivery_manager.get_current_delivery()
        
        if current_delivery:
            # Cập nhật thông tin phòng hiện tại
            self.current_room = {
                "id": current_delivery["room_id"],
                "info": current_delivery["room_info"]
            }
            # Set order data đơn giản
            self.waiting_screen.set_order_data({
                'cabinets': current_delivery["cabinets"],
                'room': self.current_room
            })
        else:
            # Tạo order đơn giản từ các tủ đã lưu
            order = {
                'cabinets': self.create_simple_cabinet_data(),
                'room': self.current_room,
            }
            self.current_order = order
            self.waiting_screen.set_order_data(order)

        try:
            from src.utils import storage
            # Tạo cấu trúc session đơn giản
            session_data = {
                'room': self.current_room,
                'cabinets': self.create_simple_cabinet_data()
            }
            storage.save_session(storage.default_session_path(), session_data)
        except Exception as _:
            pass
            
        self.stacked_widget.setCurrentIndex(3)
        
    def show_delivery_screen(self):
        """Hiển thị màn hình giao hàng"""
        # Pass room info và order data
        if self.current_room:
            room_info = self.current_room["info"]
            self.delivery_screen.set_room_info(self.current_room["id"], room_info)
            self.confirm_btn.clicked.connect(...)
            self.confirmation_screen.confirmed.connect(self.confirmed)
        if self.current_order:
            self.delivery_screen.set_order_data(self.current_order)
            
        self.stacked_widget.setCurrentIndex(6)
        
    def show_pickup_screen(self):
        """Hiển thị màn hình lấy đồ"""
        self.stacked_widget.setCurrentIndex(4)  # index của pickup_screen
        
    # ===== Active cabinet flow =====
    def show_active_open(self):
        """Đi đến màn active_cabinet: mở tủ 3s"""
        try:
            self.pickup_screen.start_opening()
        except Exception:
            pass
        self.stacked_widget.setCurrentIndex(4)
        # Sau 3s pickup_screen sẽ emit opened/closed, ta chỉ xử lý opened

    def on_active_opened(self):
        """Sau khi mở xong (3s), quay về confirmation với nút chuyển thành Close."""
        current = self.delivery_manager.get_current_delivery()
        if current:
            room_id = current["room_id"]
            cabinets = current["cabinets"]
            picked_ids = [c["id"] for c in cabinets]
        try:
            self.confirmation_screen.delivery_info_panel.set_mode_close()
            self.confirmation_screen.cabinet_panel.update_for_room(
                self.delivery_manager.get_current_delivery()["room_id"],
                [c["id"] for c in self.delivery_manager.get_current_delivery()["cabinets"]],
                picked_cabinets=[c["id"] for c in self.delivery_manager.get_current_delivery()["cabinets"]],
            )
        except Exception:
            pass
        self.stacked_widget.setCurrentIndex(5)

    def show_active_close(self):
        """Đi đến màn active_cabinet: đóng tủ 3s"""
        try:
            self.pickup_screen.start_closing()
        except Exception:
            pass
        self.stacked_widget.setCurrentIndex(4)

    def on_active_closed(self):
        """Sau khi đóng xong (3s), chuyển sang waiting cho phòng tiếp theo."""
        self.on_pickup_completed()
    def show_confirmation_screen(self):
        """Hiển thị màn hình xác nhận"""
        current_delivery = self.delivery_manager.get_current_delivery()
        if current_delivery:
            summary = {
                "room_info": current_delivery["room_info"],
                "cabinets": current_delivery["cabinets"],
                "delivery_progress": self.delivery_manager.get_delivery_progress()
            }
            self.confirmation_screen.set_delivery_summary(summary)
        self.stacked_widget.setCurrentIndex(5)
    
        
    def reset_to_emotion(self):
        """Reset về màn hình emotion"""
        self.selected_cabinets = []
        self.current_room = None
        self.current_cabinet = None
        self.current_order = None
        # Reset delivery manager
        self.delivery_manager.reset()
        self.show_emotion_screen()
    
    def create_simple_cabinet_data(self):
        """Tạo dữ liệu tủ cho session (tối đa 3 tủ, loại trùng theo id)."""
        if not self.selected_cabinets:
            return []
        seen_ids = set()
        simple_cabinets = []
        for cabinet in self.selected_cabinets:
            cab_id = cabinet.get("id")
            if not cab_id or cab_id in seen_ids:
                continue
            seen_ids.add(cab_id)
            simple_cabinets.append({
                "id": cab_id,
                "name": cabinet["info"].get("name"),
                "position": cabinet["info"].get("position"),
                "status": "locked",
                "is_open": False,
                "items_confirmed": False,
                "items_count": cabinet.get("total_items", 0)
            })
            if len(simple_cabinets) >= 3:
                break
        return simple_cabinets
    
    def reset_to_start(self):
        """Reset về màn hình đầu (giữ nguyên cho tương thích)"""
        self.reset_to_emotion()

    def handle_issue_report(self):
        """Xử lý khi người dùng báo lỗi"""
         # Có thể hiển thị dialog báo lỗi hoặc chuyển về màn hình khác
        print("Người dùng báo lỗi!")
        # Tạm thời quay về màn hình emotion
        self.reset_to_emotion()

    def on_clear_all(self):
        """Dọn toàn bộ dữ liệu tủ/đơn khi nhấn Hủy/Làm lại ở Cabinet"""
        self.selected_cabinets = []
        self.current_cabinet = None
        self.current_order = None
        try:
            from src.utils import storage
            storage.clear_session(storage.default_session_path())
        except Exception:
            pass
        
    def closeEvent(self, event):
        """Xử lý khi đóng ứng dụng"""
        # Có thể thêm logic cleanup ở đây
        event.accept()


    
    def on_confirmation_phone_call_started(self, phone_number: str):
        """Xử lý khi bắt đầu gọi điện từ confirmation screen"""
        print(f"📞 Confirmation: Đang gọi phòng {phone_number}...")
        
    def on_confirmation_phone_call_stopped(self):
        """Xử lý khi dừng cuộc gọi từ confirmation screen"""
        print("📞 Confirmation: Cuộc gọi đã dừng")
        
        # Kiểm tra nếu đã gọi đủ 3 lần mà không có phản hồi
        if hasattr(self.confirmation_screen, 'phone_call_count') and self.confirmation_screen.phone_call_count >= 3:
            print("❌ Không có phản hồi sau 3 lần gọi, bỏ qua tủ này")
            # Cập nhật trạng thái tủ sang "chưa lấy đồ" nhưng vẫn khóa
            self.update_cabinet_status_not_picked_but_locked()
            
            # Chuyển sang tủ tiếp theo (bỏ qua pickup)
            if self.delivery_manager.move_to_next_delivery():
                # Cập nhật session với tủ tiếp theo
                try:
                    from src.utils import storage
                    current_delivery = self.delivery_manager.get_current_delivery()
                    if current_delivery:
                        session_data = {
                            'room': {
                                "id": current_delivery["room_id"],
                                "info": current_delivery["room_info"]
                            },
                            'cabinets': current_delivery["cabinets"],
                        }
                        storage.save_session(storage.default_session_path(), session_data)
                        self.show_waiting_screen()
                    else:
                        self.show_emotion_screen()
                except Exception as _:
                    self.show_emotion_screen()
            else:
                # Không còn tủ nào, về emotion screen
                self.show_emotion_screen()
    
    def on_confirmation_cancelled(self):
        """Xử lý khi người dùng hủy đơn từ confirmation screen"""
        print("❌ Người dùng đã hủy đơn!")
        
        # Cập nhật trạng thái tủ sang "chưa lấy đồ" nhưng vẫn khóa
        self.update_cabinet_status_not_picked_but_locked()
        
        # Chuyển sang tủ tiếp theo (bỏ qua pickup)
        if self.delivery_manager.move_to_next_delivery():
            # Cập nhật session với tủ tiếp theo
            try:
                from src.utils import storage
                current_delivery = self.delivery_manager.get_current_delivery()
                if current_delivery:
                    session_data = {
                        'room': {
                            "id": current_delivery["room_id"],
                            "info": current_delivery["room_info"]
                        },
                        'cabinets': current_delivery["cabinets"],
                    }
                    storage.save_session(storage.default_session_path(), session_data)
                    self.show_waiting_screen()
                else:
                    self.show_emotion_screen()
            except Exception as _:
                self.show_emotion_screen()
        else:
            # Không còn tủ nào, về emotion screen
            self.show_emotion_screen()
    
    def on_items_picked(self):
        """Xử lý khi người dùng xác nhận đã lấy đồ"""
        print("✅ Người dùng đã xác nhận lấy đồ!")
        
        # Cập nhật trạng thái tủ sang "đã lấy đồ"
        self.update_cabinet_status_picked()
    
    def on_pickup_completed(self):
        """Xử lý khi pickup hoàn thành (đã lấy xong)"""
        print("✅ Pickup hoàn thành!")
        
        # Cập nhật trạng thái tủ sang "đã lấy đồ"
        self.update_cabinet_status_picked()
        
        # Đánh dấu phòng hiện tại đã hoàn thành
        self.delivery_manager.mark_current_delivery_completed()
        
        # Chuyển sang tủ/phòng tiếp theo
        if self.delivery_manager.move_to_next_delivery():
            # Còn tủ để giao, cập nhật session với tủ tiếp theo
            try:
                from src.utils import storage
                current_delivery = self.delivery_manager.get_current_delivery()
                if current_delivery:
                    session_data = {
                        'room': {
                            "id": current_delivery["room_id"],
                            "info": current_delivery["room_info"]
                        },
                        'cabinets': current_delivery["cabinets"],
                    }
                    storage.save_session(storage.default_session_path(), session_data)
                    # Chuyển sang waiting screen để robot di chuyển đến tủ tiếp theo
                    self.show_waiting_screen()
                else:
                    # Không còn tủ nào, về emotion screen
                    self.reset_to_emotion()
            except Exception as _:
                # Fallback: về emotion screen
                self.reset_to_emotion()
        else:
            # Đã giao hết tất cả tủ, xóa session và về emotion screen
            try:
                from src.utils import storage
                print("🏁 Đã hoàn thành tất cả tủ, xóa session")
                storage.clear_session(storage.default_session_path())
            except Exception as _:
                pass
            # Hiển thị màn comeback 10s rồi về emotion
            self.stacked_widget.setCurrentIndex(6)
            self.comeback_screen.start(10000)
    
    def on_cancel_task(self):
        """Xử lý khi hủy task từ pickup screen"""
        print("❌ Task đã bị hủy!")
        
        # Chuyển về màn hình setup delivery
        self.show_setup_delivery()
    
    def update_cabinet_status_picked(self):
        """Cập nhật trạng thái tủ sang đã lấy đồ"""
        current_delivery = self.delivery_manager.get_current_delivery()
        if current_delivery:
            cabinets = current_delivery["cabinets"]
            for cabinet in cabinets:
                cabinet["items_confirmed"] = True  # Đồ đã được lấy
                cabinet["is_open"] = False  # Tủ đóng lại
                cabinet["status"] = "delivered"  # Đã giao xong, không còn bị khóa
            
            # Cập nhật session
            try:
                from src.utils import storage
                session_data = {
                    'room': {
                        "id": current_delivery["room_id"],
                        "info": current_delivery["room_info"]
                    },
                    'cabinets': cabinets
                }
                storage.save_session(storage.default_session_path(), session_data)
            except Exception as _:
                pass
    
    def update_cabinet_status_not_picked(self):
        """Cập nhật trạng thái tủ sang chưa lấy đồ"""
        current_delivery = self.delivery_manager.get_current_delivery()
        if current_delivery:
            cabinets = current_delivery["cabinets"]
            for cabinet in cabinets:
                cabinet["items_confirmed"] = False  # Đồ chưa được lấy
                cabinet["is_open"] = False  # Tủ đóng lại
            
            # Cập nhật session
            try:
                from src.utils import storage
                session_data = {
                    'room': {
                        "id": current_delivery["room_id"],
                        "info": current_delivery["room_info"]
                    },
                    'cabinets': cabinets
                }
                storage.save_session(storage.default_session_path(), session_data)
            except Exception as _:
                pass
    
    def update_cabinet_status_not_picked_but_locked(self):
        """Cập nhật trạng thái tủ sang chưa lấy đồ nhưng vẫn khóa"""
        current_delivery = self.delivery_manager.get_current_delivery()
        if current_delivery:
            cabinets = current_delivery["cabinets"]
            for cabinet in cabinets:
                cabinet["items_confirmed"] = False  # Đồ chưa được lấy
                cabinet["is_open"] = False  # Tủ đóng lại
                cabinet["status"] = "locked"  # Tủ vẫn bị khóa
            
            # Cập nhật session
            try:
                from src.utils import storage
                session_data = {
                    'room': {
                        "id": current_delivery["room_id"],
                        "info": current_delivery["room_info"]
                    },
                    'cabinets': cabinets
                }
                storage.save_session(storage.default_session_path(), session_data)
            except Exception as _:
                pass


class FoodDeliveryApp:
    """Class chính quản lý ứng dụng"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.setup_app()
        
    def setup_app(self):
        """Cấu hình ứng dụng"""
        self.app.setApplicationName("Food Delivery Robot")
        self.app.setApplicationVersion("1.0")
        
        # Load config nếu có
        self.load_config()
        
    def load_config(self):
        """Load cấu hình từ file"""
        # TODO: Load từ data/config.json
        pass
        
    def run(self):
        """Chạy ứng dụng"""
        # Tạo cửa sổ chính
        self.main_window = MainWindow()
        self.main_window.show()
        
        # Bắt đầu event loop
        sys.exit(self.app.exec_())

def main():
    """Hàm chính"""
    try:
        app = FoodDeliveryApp()
        app.run()
    except Exception as e:
        print(f"Lỗi khi chạy ứng dụng: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
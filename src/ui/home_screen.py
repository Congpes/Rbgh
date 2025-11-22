"""
Home Screen - Màn hình chính theo thiết kế Figma
Layout: Đồng hồ trên giữa, icon giao hàng trái dưới, button quay về phải dưới
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QUrl
from PyQt5.QtGui import QPalette, QLinearGradient, QBrush, QColor
from PyQt5.QtCore import QFile, QTextStream
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import os
import sys
try:
    import winsound
except ImportError:
    winsound = None

# Import các component mới
from .components import ClockWidget, DeliveryIcon, BackButton
from src.services.chatbot_groq import GroqChatbot
from src.services.audio_record import AudioRecorder
from src.services.stt_vosk import VoskSTT
from src.services.stt_normalizer import STTNormalizer
from src.services.tts_piper import PiperTTS
import requests
import json

class HomeScreen(QWidget):
    """Màn hình chính theo thiết kế Figma"""
    
    # Signals - GIỮ NGUYÊN để không ảnh hưởng chức năng
    app_selected = pyqtSignal(str)  # Signal khi chọn ứng dụng (app_id)
    back_screen = pyqtSignal()      # Signal quay lại
    
    def __init__(self):
        super().__init__()
        self.setObjectName("homeScreen")
        
        # Set nền xanh đậm bằng QPalette (cách chắc chắn hơn)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(28, 20, 146))  # #1C1492
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        self.init_ui()
        self.load_styles()
        # Lazy instances
        self._chatbot = None
        self._rec = None
        self._stt = None
        self._worker = None
        self._normalizer = STTNormalizer()
        self.tts_enabled = os.getenv("ENABLE_TTS", "0") == "1"
        self._tts = None
        self._tts_worker = None
        # Khởi tạo media_player nếu TTS được bật và không có winsound
        if self.tts_enabled and (not winsound or not sys.platform.startswith("win")):
            self.media_player = QMediaPlayer()
        else:
            self.media_player = None
        
    def init_ui(self):
        """Khởi tạo giao diện theo layout Figma thực tế"""
        
        # Layout chính - vertical với spacing đẹp hơn
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(50)
        
        # 1. Đồng hồ ở giữa trên
        self.clock_widget = ClockWidget()
        main_layout.addWidget(self.clock_widget, 0, Qt.AlignTop | Qt.AlignHCenter)
        
        # 2. App component ngay dưới đồng hồ (sát trái) + text riêng
        delivery_container = QWidget()
        delivery_layout = QVBoxLayout()
        delivery_layout.setAlignment(Qt.AlignCenter)  # Căn giữa
        delivery_layout.setSpacing(5)  # GIẢM spacing xuống còn 5px (từ 15px)
        delivery_layout.setContentsMargins(0, 0, 0, 0)
        
        # Icon giao hàng
        self.delivery_icon = DeliveryIcon()
        self.delivery_icon.clicked.connect(lambda: self.app_selected.emit("delivery"))
        delivery_layout.addWidget(self.delivery_icon, 0, Qt.AlignCenter)
        
        # Text "Giao Hàng" riêng biệt - căn giữa và cách xuống
        delivery_text = QLabel("Giao Hàng")
        delivery_text.setAlignment(Qt.AlignCenter)
        delivery_text.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 14px;
                background: transparent;
                font-family: "Arial", sans-serif;
                margin-top: 5px;
                margin-bottom: 0px;
            }
        """)
        delivery_layout.addWidget(delivery_text, 0, Qt.AlignCenter)
        
        delivery_container.setLayout(delivery_layout)
        main_layout.addWidget(delivery_container, 0, Qt.AlignLeft | Qt.AlignTop)
        
        # 3. Stretch để đẩy button xuống dưới
        main_layout.addStretch()
        
        # 4. Nhóm nút hành động
        actions_row = QHBoxLayout()
        actions_row.addStretch()

        button_column = QVBoxLayout()
        button_column.setSpacing(16)
        button_column.setAlignment(Qt.AlignBottom | Qt.AlignRight)

        # 4. Nút Nghe (ghi âm -> STT -> realtime handlers -> Rasa/KB -> TTS)
        self.listen_button = QPushButton("Nhấn giữ để nói")
        self.listen_button.setStyleSheet("""
            QPushButton {
                background-color: #00A8E8;
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 10px 16px;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #0091c8; }
            QPushButton:pressed { background-color: #007aa8; }
        """)
        # Press-to-talk: mouse press -> start, mouse release -> stop & xử lý
        self.listen_button.pressed.connect(self.on_listen_press)
        self.listen_button.released.connect(self.on_listen_release)
        button_column.addWidget(self.listen_button, 0, Qt.AlignRight)

        # Nút nhập văn bản
        self.type_button = QPushButton("Nhập để hỏi")
        self.type_button.setStyleSheet("""
            QPushButton {
                background-color: #21bf73;
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 10px 16px;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #1ea565; }
            QPushButton:pressed { background-color: #198a55; }
        """)
        self.type_button.clicked.connect(self.on_type_clicked)
        button_column.addWidget(self.type_button, 0, Qt.AlignRight)

        actions_row.addLayout(button_column)

        # Bỏ hiển thị transcript trên màn hình chính

        main_layout.addLayout(actions_row)

        # 5. Button quay về ở dưới cùng (sát phải)
        self.back_button = BackButton()
        self.back_button.back_clicked.connect(self.back_screen.emit)
        main_layout.addWidget(self.back_button, 0, Qt.AlignRight)
        
        self.setLayout(main_layout)
    
    def load_styles(self):
        """Load QSS styles - đã set trực tiếp trong init_ui"""
        # Styles đã được set trực tiếp trong init_ui()
        pass
    
    def setup_fallback_background(self):
        """Fallback background nếu không load được QSS - nền xanh đậm theo Figma"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(28, 20, 146))  # #1C1492
        self.setPalette(palette)
        self.setAutoFillBackground(True)
    
    def reset(self):
        """Reset về trạng thái ban đầu"""
        pass

    # --- Hỏi/Đáp qua Rasa -> fallback KB -> TTS ---
    @property
    def chatbot(self):
        if self._chatbot is None:
            self._chatbot = GroqChatbot()
        return self._chatbot

    @property
    def tts(self):
        if not self.tts_enabled:
            raise RuntimeError("TTS đang tắt")
        if self._tts is None:
            # Đọc tốc độ từ env, mặc định 1.15 (vừa phải, không quá nhanh)
            length_scale = float(os.getenv("TTS_LENGTH_SCALE", "1.15"))
            self._tts = PiperTTS(length_scale=length_scale)
        return self._tts


    def _speak(self, answer: str) -> None:
        if not answer:
            print("TTS: Không có câu trả lời để phát")
            return
        
        print(f"TTS: Nhận câu trả lời (TTS enabled: {self.tts_enabled})")
        
        if self.tts_enabled:
            print("TTS: Bắt đầu quá trình phát âm")
            self._start_tts_worker(answer)
        else:
            print("TTS: TTS đang tắt, chỉ hiển thị text")
        
        QMessageBox.information(self, "Trả lời", answer)

    def _start_tts_worker(self, text: str) -> None:
        text = (text or "").strip()
        if not text:
            print("TTS: Text rỗng, bỏ qua")
            return
        
        print(f"TTS: Bắt đầu xử lý text (độ dài: {len(text)})")
        
        try:
            tts = self.tts
            print("TTS: Đã khởi tạo PiperTTS thành công")
        except Exception as e:
            print(f"TTS init lỗi: {e}")
            import traceback
            traceback.print_exc()
            return

        if self._tts_worker and self._tts_worker.isRunning():
            print("TTS: Dừng worker cũ")
            self._tts_worker.requestInterruption()
            self._tts_worker.quit()
            self._tts_worker.wait(200)

        print("TTS: Tạo worker mới")
        self._tts_worker = TTSWorker(text, tts)
        self._tts_worker.done.connect(self._play_tts_audio)
        self._tts_worker.error.connect(self._handle_tts_error)
        self._tts_worker.start()
        print("TTS: Worker đã được khởi động")

    def _play_tts_audio(self, wav_path: str) -> None:
        if not wav_path:
            print("TTS: Không có đường dẫn file WAV")
            return
        if not os.path.exists(wav_path):
            print(f"TTS: File không tồn tại: {wav_path}")
            return
        
        print(f"TTS: Đang phát file: {wav_path}")
        
        # Ưu tiên dùng winsound trên Windows (nhanh hơn)
        if winsound and sys.platform.startswith("win"):
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)  # Dừng âm thanh trước đó
                winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                print("TTS: Đã phát bằng winsound")
            except Exception as e:
                print(f"TTS winsound lỗi: {e}")
                # Fallback sang QMediaPlayer
                if self.media_player:
                    self._play_with_media_player(wav_path)
        elif self.media_player:
            self._play_with_media_player(wav_path)
        else:
            print("TTS: Không có phương thức phát âm nào khả dụng")
    
    def _play_with_media_player(self, wav_path: str) -> None:
        """Phát âm bằng QMediaPlayer"""
        try:
            url = QUrl.fromLocalFile(wav_path)
            if self.media_player:
                self.media_player.stop()
                self.media_player.setMedia(QMediaContent(url))
                self.media_player.setVolume(100)
                self.media_player.play()
                print("TTS: Đã phát bằng QMediaPlayer")
        except Exception as e:
            print(f"TTS QMediaPlayer lỗi: {e}")

    def _handle_tts_error(self, message: str) -> None:
        print(f"TTS lỗi: {message}")

    def on_listen_press(self):
        # Lazy init
        if self._rec is None:
            try:
                self._rec = AudioRecorder()
            except Exception as e:
                QMessageBox.warning(self, "Mic lỗi", f"Không thể khởi tạo ghi âm: {e}")
                return
        if self._stt is None:
            try:
                self._stt = VoskSTT()
            except Exception as e:
                QMessageBox.warning(self, "STT lỗi", f"Không thể khởi tạo Vosk: {e}")
                return
        try:
            self._rec.start()
        except Exception as e:
            QMessageBox.warning(self, "Ghi âm lỗi", str(e))
            return

    def on_listen_release(self):
        if self._rec is None:
            return
        try:
            wav_path = self._rec.stop()
        except Exception as e:
            QMessageBox.warning(self, "Ghi âm lỗi", str(e))
            return
        # Chạy pipeline trong luồng nền để không block UI
        self._worker = ListenWorker(wav_path, self._stt, self.chatbot, self._normalizer)
        self._worker.partial_text.connect(self._show_transcript)
        self._worker.result_ready.connect(self._speak)
        self._worker.start()

    def on_type_clicked(self):
        text, ok = QInputDialog.getText(
            self,
            "Nhập câu hỏi",
            "Bạn muốn hỏi điều gì?"
        )
        if not ok:
            return
        text = text.strip()
        if not text:
            QMessageBox.information(self, "Thông báo", "Bạn chưa nhập nội dung.")
            return

        try:
            answer = self.chatbot.chat(text)
        except Exception as e:
            answer = f"Không thể kết nối chatbot: {e}"
        self._speak(answer)

    def _show_transcript(self, text: str):
        if text:
            # Hiển thị transcript với nút báo cáo lỗi
            msg = QMessageBox()
            msg.setWindowTitle("Bạn vừa nói")
            msg.setText(f"STT nhận dạng: {text}")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Yes)
            msg.button(QMessageBox.Yes).setText("Báo cáo sai")
            msg.button(QMessageBox.Ok).setText("Đúng rồi")
            
            result = msg.exec_()
            if result == QMessageBox.Yes:
                # Báo cáo lỗi - cho phép nhập lại đúng
                correct_text, ok = QInputDialog.getText(
                    self, 
                    "Sửa lỗi STT", 
                    f"STT nhận sai: {text}\nNhập lại đúng:"
                )
                if ok and correct_text.strip():
                    self._normalizer.report_error(text, correct_text.strip())
                    QMessageBox.information(self, "Đã học", f"Đã lưu: '{text}' → '{correct_text.strip()}'")


class ListenWorker(QThread):
    result_ready = pyqtSignal(str)
    partial_text = pyqtSignal(str)

    def __init__(self, wav_path, stt, chatbot, normalizer):
        super().__init__()
        self.wav_path = wav_path
        self.stt = stt
        self.chatbot = chatbot
        self.normalizer = normalizer

    def _normalize(self, s: str) -> str:
        return self.normalizer.normalize(s)

    def _load_grammar(self):
        grammar = []
        # Đọc từ tất cả file KB
        try:
            import glob
            for kb_file in glob.glob(os.path.join("data", "kb", "*.json")):
                with open(kb_file, "r", encoding="utf-8") as f:
                    docs = json.load(f)
                    for d in docs:
                        t = (d.get("title") or "").strip()
                        if t:
                            grammar.append(t)
        except Exception:
            pass
        
        # Thêm câu phổ biến từ normalizer
        grammar += self.normalizer.get_common_phrases()
        return grammar

    def run(self):
        try:
            grammar = self._load_grammar()
            text = self.stt.transcribe_wav(self.wav_path, grammar_phrases=grammar)
            text = self._normalize(text)
            self.partial_text.emit(text)
            if not text:
                self.result_ready.emit("Xin vui lòng nói lại ạ.")
                return

            # Khởi tạo chatbot nếu chưa có
            if self.chatbot is None:
                self.chatbot = GroqChatbot()

            # Gọi Groq API
            answer = self.chatbot.chat(text)
            if not answer:
                answer = "Xin vui lòng nói lại ạ."

            self.result_ready.emit(answer)
        except Exception:
            self.result_ready.emit("Xin vui lòng nói lại ạ.")


class TTSWorker(QThread):
    done = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, text: str, tts: PiperTTS):
        super().__init__()
        self.text = text
        self.tts = tts

    def run(self):
        try:
            if self.isInterruptionRequested():
                return
            print(f"TTS: Bắt đầu tạo file âm thanh cho text: {self.text[:50]}...")
            wav_path = self.tts.synthesize(self.text)
            if self.isInterruptionRequested():
                return
            if wav_path and os.path.exists(wav_path):
                print(f"TTS: Đã tạo file thành công: {wav_path}")
                self.done.emit(wav_path)
            else:
                self.error.emit(f"File WAV không được tạo hoặc không tồn tại: {wav_path}")
        except Exception as e:
            print(f"TTS Worker lỗi: {e}")
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))
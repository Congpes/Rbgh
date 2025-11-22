"""
Màn hình quay về quầy lễ tân (Comeback) – hiển thị sau khi giao hết
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor


from src.ui.components.delivering_widget import DeliveringWidget


class ComebackScreen(QWidget):
    """Màn hình chờ 10s rồi về emotion"""

    done = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.duration_ms = 10000
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._finish)
        self._init_ui()

    def _init_ui(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#1C1492"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        main = QVBoxLayout()
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # Top title
        title = QLabel("Return to reception")
        title.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        title.setStyleSheet("color:white;background:transparent; font-size: 36px; font-weight: bold;")
        title.setMargin(30)
        main.addWidget(title, 0, Qt.AlignTop)

        # Subtitle
        subtitle = QLabel("The robot is performing a task. Please do not push it. Thank you!")
        subtitle.setAlignment(Qt.AlignHCenter)
        subtitle.setStyleSheet("color:white;background:transparent; font-size: 20px; font-weight: bold;")
        main.addWidget(subtitle, 0, Qt.AlignTop)

        # Center: vòng tròn xoay giống waiting + chữ Returning
        center_v = QVBoxLayout()
        center_v.setAlignment(Qt.AlignCenter)
        center_v.setSpacing(20)

        self.spinner = DeliveringWidget()
        self.spinner.delivering_label.setText("Returning")
        center_v.addWidget(self.spinner, 0, Qt.AlignCenter)

        center_w = QWidget()
        center_w.setLayout(center_v)
        main.addWidget(center_w, 1)

        self.setLayout(main)

    def start(self, duration_ms: int = None):
        if duration_ms is not None:
            self.duration_ms = duration_ms
        self.spinner.start_animation()
        self._timer.start(self.duration_ms)

    def _finish(self):
        self.spinner.stop_animation()
        self.done.emit()



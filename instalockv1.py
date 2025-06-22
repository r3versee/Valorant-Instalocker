import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QFont, QColor
from valclient.client import Client  # Asegúrate de que esta dependencia esté instalada y funcione con PyQt5

class ValorantAgentInstalocker:
    def __init__(self):
        self.running = True
        self.agents = {
            "jett": "add6443a-41bd-e414-f6ad-e58d267f4e95",
            "reyna": "a3bfb853-43b2-7238-a4f1-ad90e9e46bcc",
            "raze": "f94c3b30-42be-e959-889c-5aa313dba261",
            "yoru": "7f94d92c-4234-0a36-9646-3a87eb8b5c89",
            "phoenix": "eb93336a-449b-9c1b-0a54-a891f7921d69",
            "neon": "bb2a4828-46eb-8cd1-e765-15848195d751",
            "breach": "5f8d3a7f-467b-97f3-062c-13acf203c006",
            "skye": "6f2a04ca-43e0-be17-7f36-b3908627744d",
            "sova": "320b2a48-4d9b-a075-30f1-1f93a9b638fa",
            "kayo": "601dbbe7-43ce-be57-2a40-4abd24953621",
            "killjoy": "1e58de9c-4950-5125-93e9-a0aee9f98746",
            "cypher": "117ed9e3-49f3-6512-3ccf-0cada7e3823b",
            "sage": "569fdd95-4d10-43ab-ca70-79becc718b46",
            "chamber": "22697a3d-45bf-8dd7-4fec-84a9e28c69d7",
            "omen": "8e253930-4c05-31dd-1b6c-968525494517",
            "brimstone": "9f0d8ba9-4140-b941-57d3-a7ad57c6b417",
            "astra": "41fb69c1-4189-7b37-f117-bcaf1e96f1bf",
            "viper": "707eab51-4836-f488-046a-cda6bf494859",
            "fade": "dade69b4-4f5a-8528-247b-219e5a1facd6",
            "gekko": "e370fa57-4757-3604-3648-499e1f642d3f",
            "harbor": "95b78ed7-4637-86d9-7e41-71ba8c293152",
            "deadlock": "cc8b64c8-4b25-4ff9-6e7f-37b4da43d235",
            "iso": "0e38b510-41a8-5780-5e8f-568b2a4f2d6c",
            "clove": "1dbf2edd-4729-0984-3115-daa5eed44993",
            "vyse": "eb85b0c8-4258-e95e-f433-0db2e21f857"
        }
        self.seenMatches = []
        self.region = "eu"
        self.preferred_agent = "jett"
        self.status_callback = None

    def stop(self):
        self.running = False

    def set_status_callback(self, callback):
        self.status_callback = callback

    def update_status(self, message):
        if self.status_callback:
            self.status_callback(message)

    def initialize_client(self):
        while self.running:
            try:
                self.client = Client(region=self.region)
                self.client.activate()
                self.update_status("Client initialized successfully")
                self.run_instalocker()
            except Exception as e:
                self.update_status(f"Error initializing client: {e}")
            time.sleep(2)

    def run_instalocker(self):
        while self.running:
            time.sleep(1)
            try:
                session_state = self.client.fetch_presence(self.client.puuid)['sessionLoopState']
                match_id = self.client.pregame_fetch_match()['ID']

                if session_state == "PREGAME" and match_id not in self.seenMatches:
                    agent_id = self.agents[self.preferred_agent.lower()]
                    self.client.pregame_select_character(agent_id)
                    self.client.pregame_lock_character(agent_id)
                    self.seenMatches.append(match_id)
                    self.update_status(f'Successfully Locked {self.preferred_agent.capitalize()}')
            except Exception as e:
                if not self.running:
                    break
                if "pregame" not in str(e).lower():
                    self.update_status("Waiting for agent select...")

class InstalockThread(QThread):
    status_signal = pyqtSignal(str)

    def __init__(self, instalocker):
        super().__init__()
        self.instalocker = instalocker
        self.instalocker.set_status_callback(self.emit_status)

    def emit_status(self, message):
        self.status_signal.emit(message)

    def run(self):
        self.instalocker.initialize_client()

class InstalockerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(260, 320)
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
                font-family: Arial;
                font-size: 13px;
            }

            QLabel#TitleLabel {
                font-size: 11px;
                font-weight: bold;
                padding-bottom: 5px;
                color: #ffffff;
            }

            QComboBox, QPushButton {
                background-color: #1f1f1f;
                border: none;
                padding: 8px;
                border-radius: 6px;
            }

            QComboBox:hover, QPushButton:hover {
                background-color: #000080;
            }

            QPushButton#closeButton:hover {
                background-color: #ff0000;
            }

            QComboBox QAbstractItemView {
                background-color: #1f1f1f;
                selection-background-color: #000080;
                color: white;
                outline: none;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 0px;
                border: none;
            }

            QScrollBar:vertical {
                background: #1f1f1f;
                width: 8px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: #333333;
                border-radius: 4px;
            }

            QScrollBar::handle:vertical:hover {
                background: #000080;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.setup_ui()
        self.drag_position = None

        self.instalocker = ValorantAgentInstalocker()
        self.instalock_thread = None

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_label = QLabel('Valorant Instalocker <span style="color: #00ff00;">@1dekaa_</span>')
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setTextFormat(Qt.RichText)
        layout.addWidget(title_label)

        layout.addWidget(QLabel("Agent:"))

        self.agent_combo = QComboBox()
        agents = sorted([
            "Astra", "Breach", "Brimstone", "Chamber", "Clove", "Cypher", "Deadlock",
            "Fade", "Gekko", "Harbor", "Iso", "Jett", "KAY/O", "Killjoy", "Neon",
            "Omen", "Phoenix", "Raze", "Reyna", "Sage", "Skye", "Sova", "Tejo", "Viper", "Vyse", "Waylay", "Yoru"
        ])
        self.agent_combo.addItems(agents)
        self.agent_combo.setCurrentText("Jett")
        layout.addWidget(self.agent_combo)

        layout.addWidget(QLabel("Region:"))

        self.region_combo = QComboBox()
        self.region_combo.addItems(["LAN", "LAS", "BR", "EU", "NA", "AP", "KR"])
        self.region_combo.setCurrentText("EU")
        layout.addWidget(self.region_combo)

        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.toggle_instalock)
        layout.addWidget(self.start_button)

        self.close_button = QPushButton("Close")
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self.close_app)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QColor(0, 255, 0))
        font = QFont("Arial", 7)
        painter.setFont(font)
        text = ""
        text_width = painter.fontMetrics().width(text)
        text_height = painter.fontMetrics().height()
        x = self.width() - text_width - 2
        y = self.height() - 2
        painter.drawText(x, y, text)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def toggle_instalock(self):
        if self.start_button.text() == "Start":
            self.start_instalock()
        else:
            self.stop_instalock()

    def start_instalock(self):
        self.instalocker.preferred_agent = self.agent_combo.currentText().lower()
        self.instalocker.region = self.region_combo.currentText().lower()
        self.instalocker.running = True

        self.instalock_thread = InstalockThread(self.instalocker)
        self.instalock_thread.status_signal.connect(self.update_status)
        self.instalock_thread.start()

        self.start_button.setText("Stop")
        self.status_label.setText("Initializing...")

        self.agent_combo.setEnabled(False)
        self.region_combo.setEnabled(False)

    def stop_instalock(self):
        if self.instalock_thread:
            self.instalocker.stop()
            self.instalock_thread.quit()
            self.instalock_thread.wait()

        self.start_button.setText("Start")
        self.status_label.setText("Stopped")

        self.agent_combo.setEnabled(True)
        self.region_combo.setEnabled(True)

    def update_status(self, message):
        self.status_label.setText(message)

    def close_app(self):
        self.stop_instalock()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InstalockerUI()
    window.show()
    sys.exit(app.exec_())

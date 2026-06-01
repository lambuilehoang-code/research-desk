from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QFrame


class InputBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(320)
        self.setMaximumWidth(680)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.island = QFrame()
        self.island.setObjectName("inputIsland")
        self.island.setFixedHeight(56)
        island_layout = QHBoxLayout(self.island)
        island_layout.setContentsMargins(16, 8, 8, 8)
        island_layout.setSpacing(10)

        self.input = QLineEdit()
        self.input.setObjectName("chatInput")
        self.input.setPlaceholderText("Ask a research question...")
        self.input.setFrame(False)

        self.send_btn = QPushButton("↑")
        self.send_btn.setObjectName("sendBtn")
        self.send_btn.setFixedSize(40, 40)

        island_layout.addWidget(self.input, stretch=1)
        island_layout.addWidget(self.send_btn)

        outer.addWidget(self.island)

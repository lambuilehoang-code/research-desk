from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QFrame,
)


class NotebookPanel(QWidget):
    """Outline / notebook picker — visible on Notebook nav."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(240)
        self.setMaximumWidth(300)
        self.setObjectName("notebookPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Outline")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        nb_title = QLabel("NOTEBOOKS")
        nb_title.setObjectName("sectionTitle")
        layout.addWidget(nb_title)

        nb_card = QFrame()
        nb_card.setObjectName("panelCard")
        nb_card_layout = QVBoxLayout(nb_card)
        nb_card_layout.setContentsMargins(8, 8, 8, 8)
        self.notebook_list = QListWidget()
        self.notebook_list.setFrameShape(QListWidget.Shape.NoFrame)
        self.notebook_list.setObjectName("outlineList")
        self.notebook_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        nb_card_layout.addWidget(self.notebook_list)
        layout.addWidget(nb_card, stretch=1)

        rep_title = QLabel("REPORTS")
        rep_title.setObjectName("sectionTitle")
        layout.addWidget(rep_title)

        rep_card = QFrame()
        rep_card.setObjectName("panelCard")
        rep_card_layout = QVBoxLayout(rep_card)
        rep_card_layout.setContentsMargins(8, 8, 8, 8)
        self.report_list = QListWidget()
        self.report_list.setFrameShape(QListWidget.Shape.NoFrame)
        self.report_list.setObjectName("outlineList")
        self.report_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        rep_card_layout.addWidget(self.report_list)
        layout.addWidget(rep_card, stretch=1)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setObjectName("secondary")
        layout.addWidget(self.refresh_btn)

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout


class SourceCard(QFrame):
    """Single source reference card for the Notebook Reference panel."""

    clicked = pyqtSignal(int)

    def __init__(
        self,
        index: int,
        title: str,
        excerpt: str,
        tags: list[str] | None = None,
        url: str = "",
        detail: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("sourceCard")
        self.index = index
        self.card_title = title
        self.card_excerpt = excerpt
        self.card_url = url
        self.card_detail = detail or excerpt
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        header = QLabel(f"SOURCE {index:02d}")
        header.setObjectName("sourceIndex")
        layout.addWidget(header)

        title_lbl = QLabel(title)
        title_lbl.setWordWrap(True)
        title_lbl.setMinimumWidth(0)
        title_lbl.setObjectName("sourceTitle")
        layout.addWidget(title_lbl)

        if excerpt:
            excerpt_lbl = QLabel(excerpt)
            excerpt_lbl.setWordWrap(True)
            excerpt_lbl.setMinimumWidth(0)
            excerpt_lbl.setObjectName("sourceExcerpt")
            layout.addWidget(excerpt_lbl)

        if tags:
            tag_row = QHBoxLayout()
            tag_row.setSpacing(6)
            for tag in tags[:4]:
                chip = QLabel(tag.upper())
                chip.setObjectName("tagChip")
                tag_row.addWidget(chip)
            tag_row.addStretch()
            layout.addLayout(tag_row)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.index)
        super().mouseReleaseEvent(event)

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox


class SourceDetailDialog(QDialog):
    """Modal detail view for a notebook source or synthesis excerpt."""

    def __init__(self, title: str, text: str, parent=None):
        super().__init__(parent)
        self.setObjectName("sourceDetailDialog")
        self.setWindowTitle(title)
        self.setMinimumSize(480, 320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        body = QTextEdit()
        body.setObjectName("sourceDetailBody")
        body.setReadOnly(True)
        body.setPlainText(text)
        layout.addWidget(body, stretch=1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

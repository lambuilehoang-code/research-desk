import os
from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)


class ReportPickerDialog(QDialog):
    """Pick a saved report from the reports/ folder."""

    view_in_app = pyqtSignal(str)

    def __init__(self, report_paths: list[Path], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Browse reports")
        self.setObjectName("reportPickerDialog")
        self.setMinimumSize(520, 420)
        self._paths = report_paths

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        hint = QLabel("Select a report from AIResearch/reports/")
        hint.setObjectName("documentMeta")
        layout.addWidget(hint)

        self.list = QListWidget()
        self.list.setObjectName("outlineList")
        for path in report_paths:
            item = QListWidgetItem(path.name)
            item.setData(256, str(path))
            self.list.addItem(item)
        if self.list.count():
            self.list.setCurrentRow(0)
        self.list.itemDoubleClicked.connect(self._view_in_app)
        layout.addWidget(self.list, stretch=1)

        btn_row = QHBoxLayout()
        self.open_file_btn = QDialogButtonBox()
        open_btn = self.open_file_btn.addButton(
            "Open file", QDialogButtonBox.ButtonRole.ActionRole
        )
        view_btn = self.open_file_btn.addButton(
            "View in app", QDialogButtonBox.ButtonRole.ActionRole
        )
        close_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_box.rejected.connect(self.reject)
        btn_row.addWidget(self.open_file_btn)
        btn_row.addStretch()
        btn_row.addWidget(close_box)
        layout.addLayout(btn_row)

        open_btn.clicked.connect(self._open_file)
        view_btn.clicked.connect(self._view_in_app)

    def _selected_path(self) -> Path | None:
        item = self.list.currentItem()
        if not item:
            return None
        return Path(item.data(256))

    def _open_file(self):
        path = self._selected_path()
        if not path:
            return
        if not path.exists():
            return
        os.startfile(path)
        self.accept()

    def _view_in_app(self):
        path = self._selected_path()
        if not path or not path.exists():
            return
        self.view_in_app.emit(str(path))
        self.accept()

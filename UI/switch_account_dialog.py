import research_agent as agent
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class SwitchAccountDialog(QDialog):
    """Switch Google account in Chromium; saved accounts stay in the browser profile."""

    account_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Đổi tài khoản NotebookLM")
        self.setMinimumWidth(480)
        self.setObjectName("settingsDialog")

        layout = QVBoxLayout(self)

        intro = QLabel(
            "Tài khoản Google được lưu trong trình duyệt Chromium của NotebookLM.\n"
            "Lần sau mở lại, chọn nhanh tài khoản cũ — không cần đăng nhập lại."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        self.session_label = QLabel()
        self.session_label.setObjectName("documentMeta")
        layout.addWidget(self.session_label)

        layout.addWidget(QLabel("Tài khoản đã lưu trên máy:"))
        self.accounts_list = QListWidget()
        self.accounts_list.setMinimumHeight(100)
        layout.addWidget(self.accounts_list)

        steps = QLabel(
            "1. Bấm <b>Mở Chromium</b>\n"
            "2. Trong cửa sổ: ảnh Google → chọn tài khoản khác hoặc <b>Thêm tài khoản</b>\n"
            "3. Vào trang NotebookLM → bấm <b>Enter</b> trong cửa sổ terminal\n"
            "4. Bấm <b>Xong — tải notebook</b> ở đây"
        )
        steps.setWordWrap(True)
        steps.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(steps)

        self.fresh_check = QCheckBox(
            "Xóa toàn bộ session cũ (--fresh) — chỉ khi bị lỗi hoặc muốn đăng xuất hết"
        )
        layout.addWidget(self.fresh_check)

        self.open_btn = QPushButton("Mở Chromium")
        self.open_btn.clicked.connect(self._open_chromium)
        layout.addWidget(self.open_btn)

        self.done_btn = QPushButton("Xong — tải notebook")
        self.done_btn.setObjectName("secondary")
        self.done_btn.clicked.connect(self._done)
        layout.addWidget(self.done_btn)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn = buttons.button(QDialogButtonBox.StandardButton.Close)
        if close_btn:
            close_btn.clicked.connect(self.reject)
        layout.addWidget(buttons)

        self._refresh_accounts()

    def _refresh_accounts(self):
        self.accounts_list.clear()
        active = agent.get_active_google_account_hint()
        saved = agent.get_saved_google_accounts()

        if active:
            self.session_label.setText(f"Đang dùng: {active}")
        else:
            self.session_label.setText("Chưa đăng nhập hoặc chưa xác định được email.")

        if saved:
            for email in saved:
                marker = "★ " if active and email.lower() == active.lower() else "   "
                self.accounts_list.addItem(QListWidgetItem(f"{marker}{email}"))
        else:
            self.accounts_list.addItem(
                QListWidgetItem("(Chưa có — mở Chromium và đăng nhập lần đầu)")
            )

    def _open_chromium(self):
        fresh = self.fresh_check.isChecked()
        if fresh:
            reply = QMessageBox.question(
                self,
                "Xóa session cũ?",
                "Mọi tài khoản đã lưu trong Chromium sẽ bị xóa.\nTiếp tục?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        agent.launch_notebooklm_switch_account(fresh=fresh)
        QMessageBox.information(
            self,
            "Chromium",
            "Cửa sổ terminal + Chromium sẽ mở.\n\n"
            "Đổi hoặc thêm tài khoản Google trong trình duyệt,\n"
            "rồi bấm Enter trong terminal.\n\n"
            "Trong lúc đó không bấm Refresh ở app.",
        )

    def _done(self):
        self.account_changed.emit()
        self._refresh_accounts()
        QMessageBox.information(
            self,
            "Đã cập nhật",
            "Notebook sẽ được tải lại với tài khoản vừa chọn.",
        )
        self.accept()

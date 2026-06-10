import research_agent as agent
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class AccountsDialog(QDialog):
    """Manage multiple NotebookLM Google accounts (CLI profiles)."""

    accounts_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("NotebookLM accounts")
        self.setMinimumWidth(520)
        self.setObjectName("settingsDialog")

        layout = QVBoxLayout(self)

        hint = QLabel(
            "Each account is a saved profile. Switch anytime — no logout needed.\n"
            "To add an account: create a profile → sign in with Google in Chrome → "
            "Sign in (Chrome)."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.active_label = QLabel()
        self.active_label.setObjectName("documentMeta")
        layout.addWidget(self.active_label)

        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(160)
        layout.addWidget(self.list_widget)

        add_row = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("New account name, e.g. work or personal")
        add_row.addWidget(self.name_input, stretch=1)
        self.add_btn = QPushButton("Add account")
        self.add_btn.setObjectName("secondary")
        self.add_btn.clicked.connect(self._add_account)
        add_row.addWidget(self.add_btn)
        layout.addLayout(add_row)

        btn_row = QHBoxLayout()
        self.switch_btn = QPushButton("Use selected")
        self.switch_btn.clicked.connect(self._switch_account)
        self.signin_btn = QPushButton("Sign in (Chrome)")
        self.signin_btn.clicked.connect(self._sign_in_chrome)
        self.signin_browser_btn = QPushButton("Sign in (browser window)")
        self.signin_browser_btn.setObjectName("secondary")
        self.signin_browser_btn.clicked.connect(self._sign_in_browser)
        btn_row.addWidget(self.switch_btn)
        btn_row.addWidget(self.signin_btn)
        btn_row.addWidget(self.signin_browser_btn)
        layout.addLayout(btn_row)

        chrome_hint = QLabel(
            "Chrome sign-in: open Chrome → log into the Google account you want → "
            "notebooklm.google.com → then click Sign in (Chrome)."
        )
        chrome_hint.setWordWrap(True)
        chrome_hint.setObjectName("documentMeta")
        layout.addWidget(chrome_hint)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        close_btn = buttons.button(QDialogButtonBox.StandardButton.Close)
        if close_btn:
            close_btn.clicked.connect(self.accept)
        layout.addWidget(buttons)

        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        profiles = agent.list_notebooklm_profiles()
        active = agent.get_notebooklm_profile()

        if not profiles:
            item = QListWidgetItem("default — (run Sign in to authenticate)")
            item.setData(Qt.ItemDataRole.UserRole, "default")
            self.list_widget.addItem(item)
        else:
            for p in profiles:
                name = p.get("name", "")
                if p.get("authenticated"):
                    status = "signed in"
                else:
                    status = "not signed in"
                marker = "★ " if name == active else ""
                item = QListWidgetItem(f"{marker}{name} — {status}")
                item.setData(Qt.ItemDataRole.UserRole, name)
                self.list_widget.addItem(item)
                if name == active:
                    self.list_widget.setCurrentItem(item)

        self.active_label.setText(f"Active account: {active}")

    def _selected_profile(self) -> str | None:
        item = self.list_widget.currentItem()
        if not item:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def _add_account(self):
        name = self.name_input.text().strip()
        err = agent.validate_profile_name(name)
        if err:
            QMessageBox.warning(self, "Invalid name", err)
            return

        ok, msg = agent.create_notebooklm_profile(name)
        if not ok:
            QMessageBox.warning(self, "Could not create", msg)
            return

        ok, msg = agent.set_notebooklm_profile(name)
        if not ok:
            QMessageBox.warning(self, "Created but not active", msg)
        else:
            self.name_input.clear()

        self.refresh_list()
        self.accounts_changed.emit()

        QMessageBox.information(
            self,
            "Account added",
            f"Profile '{name}' is ready.\n\n"
            "1. Open Chrome and sign into the Google account you want.\n"
            "2. Visit notebooklm.google.com in that Chrome profile.\n"
            "3. Click Sign in (Chrome) in this dialog.\n"
            "4. Click Refresh in the app.",
        )

    def _switch_account(self):
        name = self._selected_profile()
        if not name:
            QMessageBox.information(self, "Select account", "Pick an account from the list.")
            return

        ok, msg = agent.set_notebooklm_profile(name)
        if not ok:
            QMessageBox.warning(self, "Switch failed", msg)
            return

        self.refresh_list()
        self.accounts_changed.emit()
        QMessageBox.information(
            self,
            "Account switched",
            f"Now using '{name}'. Click Refresh to load notebooks.",
        )

    def _sign_in_chrome(self):
        name = self._selected_profile() or agent.get_notebooklm_profile()
        agent.set_notebooklm_profile(name)
        agent.launch_notebooklm_login(name, browser_cookies=True)
        QMessageBox.information(
            self,
            "Sign in with Chrome",
            "A terminal window will read cookies from Chrome.\n\n"
            "Make sure Chrome is logged into the correct Google account, "
            "then return here and click Refresh.",
        )

    def _sign_in_browser(self):
        name = self._selected_profile() or agent.get_notebooklm_profile()
        agent.set_notebooklm_profile(name)
        agent.launch_notebooklm_login(name, browser_cookies=False)
        QMessageBox.information(
            self,
            "Browser sign-in",
            "Close Research Desk first if browser login fails to open.\n\n"
            "Complete Google login in the browser window, press ENTER in the "
            "terminal, then Refresh.",
        )

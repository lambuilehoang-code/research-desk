from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QLineEdit


class TopBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(56)
        self.setObjectName("topBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(10)

        self.breadcrumb = QLabel("Research Desk  |  Chat")
        self.breadcrumb.setObjectName("breadcrumb")
        layout.addWidget(self.breadcrumb)

        layout.addStretch()

        self.search = QLineEdit()
        self.search.setObjectName("searchBar")
        self.search.setPlaceholderText("Search notebooks, reports, sources...")
        self.search.setMinimumWidth(160)
        self.search.setMaximumWidth(300)
        layout.addWidget(self.search)

        self.status_label = QLabel("")
        self.status_label.setObjectName("topPill")
        layout.addWidget(self.status_label)

        self.login_btn = QPushButton("Login")
        self.login_btn.setObjectName("topPill")
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setObjectName("topPill")
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setObjectName("topPill")
        layout.addWidget(self.login_btn)
        layout.addWidget(self.refresh_btn)
        layout.addWidget(self.settings_btn)

    def set_status(self, text: str):
        self.status_label.setText(text or "")

    def set_breadcrumb(self, text: str):
        self.breadcrumb.setText(text)

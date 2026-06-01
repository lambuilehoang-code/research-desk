from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

from UI.nav_icons import nav_icon


class AppSidebar(QWidget):
    """Full-height Stitch-style navigation sidebar."""

    view_changed = pyqtSignal(str)

    _NAV = [
        ("sources", "Sources"),
        ("chat", "Chat"),
        ("analysis", "Analysis"),
        ("notebook", "Notebook"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(240)
        self.setObjectName("appSidebar")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 24, 20, 24)
        layout.setSpacing(6)

        brand = QLabel("Research Desk")
        brand.setObjectName("brandTitle")
        subtitle = QLabel("AI Synthesis")
        subtitle.setObjectName("brandSubtitle")
        layout.addWidget(brand)
        layout.addWidget(subtitle)
        layout.addSpacing(16)

        self.new_project_btn = QPushButton("  New Project")
        self.new_project_btn.setObjectName("primary")
        self.new_project_btn.setIcon(nav_icon("notebook"))
        self.new_project_btn.setFixedHeight(44)
        layout.addWidget(self.new_project_btn)
        layout.addSpacing(20)

        self._buttons: dict[str, QPushButton] = {}
        for view_id, label in self._NAV:
            btn = QPushButton(f"  {label}")
            btn.setObjectName("navItem")
            btn.setCheckable(True)
            btn.setFixedHeight(40)
            btn.setIcon(nav_icon(view_id))
            btn.clicked.connect(lambda checked, v=view_id: self._select(v))
            layout.addWidget(btn)
            self._buttons[view_id] = btn

        layout.addStretch()

        self.settings_btn = QPushButton("  Settings")
        self.settings_btn.setObjectName("navItem")
        self.settings_btn.setCheckable(True)
        self.settings_btn.setFixedHeight(40)
        self.settings_btn.setIcon(nav_icon("settings"))
        self.settings_btn.clicked.connect(lambda: self._select("settings"))
        layout.addWidget(self.settings_btn)
        self._buttons["settings"] = self.settings_btn

        layout.addSpacing(12)
        user_name = QLabel("Research User")
        user_name.setObjectName("userName")
        user_role = QLabel("Analyst")
        user_role.setObjectName("userRole")
        layout.addWidget(user_name)
        layout.addWidget(user_role)

        self._select("chat")

    def select_view(self, view_id: str):
        self._select(view_id)

    def _select(self, view_id: str):
        for vid, btn in self._buttons.items():
            btn.setChecked(vid == view_id)
        self.view_changed.emit(view_id)

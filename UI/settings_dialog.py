import research_agent as agent
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings — one-time setup")
        self.setMinimumWidth(480)
        self.setObjectName("settingsDialog")

        layout = QFormLayout(self)

        hint = QLabel(
            "Free AI via OpenRouter (not Anthropic direct).\n"
            "Get a free key: https://openrouter.ai/settings/keys"
        )
        hint.setWordWrap(True)
        layout.addRow(hint)

        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText("sk-or-v1-...")
        if agent.OPENROUTER_API_KEY:
            self.key_input.setText(agent.OPENROUTER_API_KEY)
        layout.addRow("OpenRouter API key:", self.key_input)

        self.model_input = QLineEdit(agent.CLAUDE_MODEL)
        self.model_input.setPlaceholderText("openrouter/free")
        layout.addRow("Model:", self.model_input)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["vi", "en"])
        idx = self.lang_combo.findText(agent.LANGUAGE)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        layout.addRow(
            "Default language (fallback):",
            self.lang_combo,
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def save(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "Missing key", "Paste your OpenRouter API key.")
            return False
        agent.save_env_settings(
            api_key=key,
            model=self.model_input.text().strip() or "openrouter/free",
            language=self.lang_combo.currentText(),
            notebooklm_profile=agent.get_notebooklm_profile(),
        )
        return True

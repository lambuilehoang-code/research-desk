from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QListWidget,
    QListWidgetItem,
    QHBoxLayout,
)

import research_agent as agent


class AnalysisPanel(QWidget):
    """Dashboard of local research stats and recent reports."""

    report_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("documentPanel")
        self._reports: list = []
        self._conversations: list = []
        self._search_query = ""
        self._notebook_id = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(48, 32, 48, 32)
        outer.setSpacing(16)

        title = QLabel("Analysis")
        title.setObjectName("documentTitle")
        self.subtitle = QLabel("Overview of saved reports and chat history.")
        self.subtitle.setObjectName("documentMeta")
        self.subtitle.setWordWrap(True)
        outer.addWidget(title)
        outer.addWidget(self.subtitle)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        self.reports_chip = QLabel("Reports: 0")
        self.reports_chip.setObjectName("statChip")
        self.conversations_chip = QLabel("Conversations: 0")
        self.conversations_chip.setObjectName("statChip")
        self.notebook_chip = QLabel("Notebook: —")
        self.notebook_chip.setObjectName("statChip")
        stats_row.addWidget(self.reports_chip)
        stats_row.addWidget(self.conversations_chip)
        stats_row.addWidget(self.notebook_chip)
        stats_row.addStretch()
        outer.addLayout(stats_row)

        reports_card = QFrame()
        reports_card.setObjectName("panelCard")
        reports_layout = QVBoxLayout(reports_card)
        reports_layout.setContentsMargins(16, 16, 16, 16)
        reports_layout.addWidget(QLabel("Recent reports"))
        self.report_list = QListWidget()
        self.report_list.setObjectName("outlineList")
        self.report_list.setFrameShape(QListWidget.Shape.NoFrame)
        self.report_list.itemClicked.connect(self._on_report_clicked)
        reports_layout.addWidget(self.report_list)
        outer.addWidget(reports_card, stretch=1)

        conv_card = QFrame()
        conv_card.setObjectName("panelCard")
        conv_layout = QVBoxLayout(conv_card)
        conv_layout.setContentsMargins(16, 16, 16, 16)
        conv_layout.addWidget(QLabel("Recent questions"))
        self.conv_list = QListWidget()
        self.conv_list.setObjectName("outlineList")
        self.conv_list.setFrameShape(QListWidget.Shape.NoFrame)
        conv_layout.addWidget(self.conv_list)
        outer.addWidget(conv_card, stretch=1)

    def _matches(self, text: str) -> bool:
        if not self._search_query:
            return True
        return self._search_query in text.lower()

    def _on_report_clicked(self, item):
        path = item.data(256)
        if path:
            self.report_clicked.emit(str(path))

    def apply_search(self, query: str):
        self._search_query = query.strip().lower()
        self._render_lists()

    def refresh(self, notebook_id: str | None, notebook_title: str = ""):
        self._notebook_id = notebook_id
        self._reports = list(agent.list_report_files())
        self.reports_chip.setText(f"Reports: {len(self._reports)}")

        if notebook_id:
            self._conversations = agent.list_all_conversations(notebook_id)
            stats = agent.get_conversation_stats(notebook_id)
            self.conversations_chip.setText(f"Messages: {stats.get('msg_count', 0)}")
            self.notebook_chip.setText(f"Notebook: {notebook_title or 'Selected'}")
        else:
            self._conversations = []
            self.conversations_chip.setText("Conversations: 0")
            self.notebook_chip.setText("Notebook: none selected")

        self._render_lists()

    def _render_lists(self):
        self.report_list.clear()
        shown = 0
        for path in self._reports:
            if not self._matches(path.name):
                continue
            item = QListWidgetItem(path.name)
            item.setData(256, str(path))
            self.report_list.addItem(item)
            shown += 1
            if shown >= 10 and not self._search_query:
                break
        if not shown:
            self.report_list.addItem(
                "No matching reports." if self._search_query else "No reports yet."
            )

        self.conv_list.clear()
        if not self._notebook_id:
            self.conv_list.addItem("Select a notebook to see question history.")
            return
        if not self._conversations:
            self.conv_list.addItem(
                "No matching questions."
                if self._search_query
                else "No questions yet for this notebook."
            )
            return

        shown_conv = 0
        for conv in self._conversations:
            question = conv.get("question", "(untitled)")
            if not self._matches(question):
                continue
            self.conv_list.addItem(question)
            shown_conv += 1
            if shown_conv >= 8 and not self._search_query:
                break
        if not shown_conv:
            self.conv_list.addItem("No matching questions.")

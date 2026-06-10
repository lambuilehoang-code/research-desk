from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QApplication,
    QMessageBox,
    QDialog,
    QListWidgetItem,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontMetrics
import research_agent as agent
from UI.workers import ResearchWorker

from UI.topbar import TopBar
from UI.app_sidebar import AppSidebar
from UI.notebook_panel import NotebookPanel
from UI.document_panel import DocumentPanel
from UI.context_panel import ContextPanel
from UI.input_bar import InputBar
from UI.source_hub_panel import SourceHubPanel
from UI.analysis_panel import AnalysisPanel
from UI.settings_dialog import SettingsDialog
from UI.report_picker_dialog import ReportPickerDialog
from UI.accounts_dialog import AccountsDialog

PROJECT_DIR = Path(__file__).resolve().parent.parent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Research Desk")
        self.resize(1440, 900)
        self.setMinimumSize(1400, 720)

        self.notebook_id = None
        self.notebooks = []
        self.report_paths = []
        self.worker = None
        self.last_report_path = None
        self._last_view = "chat"
        self._current_notebook_title = ""
        self._search_query = ""

        central = QWidget()
        central.setObjectName("appRoot")
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.app_sidebar = AppSidebar()
        root.addWidget(self.app_sidebar)

        main_column = QWidget()
        main_column.setObjectName("mainColumn")
        main_layout = QVBoxLayout(main_column)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.topbar = TopBar()
        main_layout.addWidget(self.topbar)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)

        self.notebook_panel = NotebookPanel()
        self.notebook_panel.hide()

        self.document = DocumentPanel()
        self.context = ContextPanel()
        self.input_bar = InputBar()

        doc_column = QWidget()
        doc_column.setObjectName("documentPanel")
        doc_layout = QVBoxLayout(doc_column)
        doc_layout.setContentsMargins(0, 0, 0, 0)
        doc_layout.setSpacing(0)
        doc_layout.addWidget(self.document, stretch=1)

        input_row = QHBoxLayout()
        input_row.setContentsMargins(48, 0, 48, 24)
        input_row.addStretch()
        input_row.addWidget(self.input_bar)
        input_row.addStretch()
        doc_layout.addLayout(input_row)

        self.source_hub = SourceHubPanel()
        self.analysis_panel = AnalysisPanel()

        self.view_stack = QStackedWidget()
        self.view_stack.addWidget(doc_column)
        self.view_stack.addWidget(self.source_hub)
        self.view_stack.addWidget(self.analysis_panel)

        content.addWidget(self.notebook_panel)
        content.addWidget(self.view_stack, stretch=1)
        content.addWidget(self.context)
        main_layout.addLayout(content, stretch=1)

        root.addWidget(main_column, stretch=1)

        self.input_bar.send_btn.clicked.connect(self.send_question)
        self.input_bar.input.returnPressed.connect(self.send_question)

        self.topbar.refresh_btn.clicked.connect(self.load_notebooks)
        self.topbar.login_btn.clicked.connect(self.open_accounts)
        self.topbar.settings_btn.clicked.connect(self.open_settings)
        self.notebook_panel.refresh_btn.clicked.connect(self.load_notebooks)
        self.notebook_panel.notebook_list.currentRowChanged.connect(
            self.on_notebook_selected
        )
        self.notebook_panel.report_list.currentRowChanged.connect(
            self.on_report_selected
        )
        self.context.browse_reports_requested.connect(self.browse_reports)
        self.app_sidebar.view_changed.connect(self.on_nav_changed)
        self.app_sidebar.new_project_btn.clicked.connect(self.new_project)
        self.analysis_panel.report_clicked.connect(self.open_report_file)
        self.topbar.search.textChanged.connect(self.on_search_changed)

        self._load_theme()
        try:
            self.load_notebooks()
        except Exception:
            self.topbar.set_status("Could not load notebooks — Login then Refresh")
        self.load_reports()
        self.refresh_credits()
        self.topbar.set_status(f"Ready · account: {agent.get_notebooklm_profile()}")
        self.on_nav_changed("chat")

    def _load_theme(self):
        qss_path = PROJECT_DIR / "Styles" / "theme.qss"
        if qss_path.exists():
            self.setStyleSheet(qss_path.read_text(encoding="utf-8"))

    def on_search_changed(self, text: str):
        self._search_query = text.strip().lower()
        self._populate_notebook_list()
        self._populate_report_list()
        self.source_hub.apply_search(text)
        self.analysis_panel.apply_search(text)

    def _populate_notebook_list(self):
        self.notebook_panel.notebook_list.blockSignals(True)
        self.notebook_panel.notebook_list.clear()
        current_row = -1
        shown = 0
        metrics = QFontMetrics(self.notebook_panel.notebook_list.font())
        list_width = max(180, self.notebook_panel.notebook_list.width() - 24)
        for i, nb in enumerate(self.notebooks):
            title = nb.get("title") or "(Untitled)"
            if self._search_query and self._search_query not in title.lower():
                continue
            label = metrics.elidedText(title, Qt.TextElideMode.ElideMiddle, list_width)
            item = QListWidgetItem(label)
            item.setToolTip(title)
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.notebook_panel.notebook_list.addItem(item)
            if self.notebook_id and nb.get("id") == self.notebook_id:
                current_row = shown
            shown += 1
        if current_row >= 0:
            self.notebook_panel.notebook_list.setCurrentRow(current_row)
        elif shown and self.notebook_panel.notebook_list.currentRow() < 0:
            self.notebook_panel.notebook_list.setCurrentRow(0)
        self.notebook_panel.notebook_list.blockSignals(False)

    def _populate_report_list(self):
        self.notebook_panel.report_list.blockSignals(True)
        self.notebook_panel.report_list.clear()
        metrics = QFontMetrics(self.notebook_panel.report_list.font())
        list_width = max(180, self.notebook_panel.report_list.width() - 24)
        for i, path in enumerate(self.report_paths):
            if self._search_query and self._search_query not in path.name.lower():
                continue
            label = metrics.elidedText(
                path.name, Qt.TextElideMode.ElideMiddle, list_width
            )
            item = QListWidgetItem(label)
            item.setToolTip(path.name)
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.notebook_panel.report_list.addItem(item)
        self.notebook_panel.report_list.blockSignals(False)

    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.save():
            self.topbar.set_status(f"Settings saved — {agent.CLAUDE_MODEL}")
            self.refresh_credits()

    def new_project(self):
        self.document.reset_welcome()
        self.context.clear()
        self.app_sidebar.select_view("notebook")
        self.topbar.set_status("Select a notebook to start a new project")

    def browse_reports(self):
        self.load_reports()
        if not self.report_paths:
            QMessageBox.information(
                self,
                "No reports",
                "No saved reports in the reports/ folder yet.",
            )
            return
        dlg = ReportPickerDialog(self.report_paths, self)
        dlg.view_in_app.connect(self.open_report_file)
        dlg.exec()

    def open_report_file(self, path_str: str):
        path = Path(path_str)
        if not path.exists():
            QMessageBox.warning(self, "Missing file", f"Report not found:\n{path}")
            return
        self.last_report_path = str(path)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as e:
            self.topbar.set_status(f"Could not read report: {e}")
            return
        self.document.show_report(text)
        self.context.show_report_sources(text)
        self.topbar.set_status(f"Opened: {path.name}")
        self.app_sidebar.select_view("chat")

    def on_nav_changed(self, view_id: str):
        if view_id == "settings":
            self.open_settings()
            self.app_sidebar.select_view(self._last_view)
            return

        self._last_view = view_id

        crumbs = {
            "chat": "Research Desk  |  Chat",
            "notebook": "Research Desk  |  Notebook",
            "sources": "Research Desk  |  Sources",
            "analysis": "Research Desk  |  Analysis",
        }
        self.topbar.set_breadcrumb(crumbs.get(view_id, "Research Desk"))

        show_notebook_col = view_id == "notebook"
        self.notebook_panel.setVisible(show_notebook_col)

        stack_map = {
            "chat": 0,
            "notebook": 0,
            "sources": 1,
            "analysis": 2,
        }
        self.view_stack.setCurrentIndex(stack_map.get(view_id, 0))
        self.context.setVisible(view_id in ("chat", "notebook"))

        if view_id == "sources":
            self.load_sources_for_hub()
        elif view_id == "analysis":
            self.refresh_analysis()

    def load_notebooks(self):
        self.topbar.set_status("Loading notebooks...")
        QApplication.processEvents()

        notebooks = agent.fetch_notebooks()
        self.notebook_panel.notebook_list.clear()
        self.notebook_id = None
        self._current_notebook_title = ""

        if notebooks is None:
            self.topbar.set_status("Could not load notebooks — try Login then Refresh")
            self.notebooks = []
            return

        self.notebooks = notebooks
        if not self.notebooks:
            self.topbar.set_status("No notebooks — Login then Refresh")
            return

        self._populate_notebook_list()
        if self.notebook_panel.notebook_list.count():
            self.notebook_panel.notebook_list.setCurrentRow(0)
        self.topbar.set_status(
            f"{len(self.notebooks)} notebooks · account: {agent.get_notebooklm_profile()}"
        )
        self.load_reports()

    def on_notebook_selected(self, row: int):
        item = self.notebook_panel.notebook_list.item(row)
        if not item:
            self.notebook_id = None
            self._current_notebook_title = ""
            return
        idx = item.data(Qt.ItemDataRole.UserRole)
        if idx is None or idx < 0 or idx >= len(self.notebooks):
            self.notebook_id = None
            self._current_notebook_title = ""
            return
        nb = self.notebooks[idx]
        self.notebook_id = nb["id"]
        title = nb.get("title") or "(Untitled)"
        self._current_notebook_title = title
        self.document.set_notebook(title)
        self.topbar.set_status(f"Notebook: {title}")

        if self._last_view == "sources":
            self.load_sources_for_hub()
        elif self._last_view == "analysis":
            self.refresh_analysis()

    def load_sources_for_hub(self):
        if not self.notebook_id:
            self.source_hub.show_message(
                "No notebook selected. Open Notebook, pick one, then Refresh."
            )
            return

        self.source_hub.show_loading(self._current_notebook_title)
        QApplication.processEvents()

        sources = agent.fetch_sources(self.notebook_id)
        if sources is None:
            self.source_hub.show_message(
                "Could not load sources. Try Login NotebookLM, then Refresh."
            )
            return

        self.source_hub.load_sources(sources, self._current_notebook_title)

    def refresh_analysis(self):
        self.analysis_panel.refresh(self.notebook_id, self._current_notebook_title)

    def open_accounts(self):
        dlg = AccountsDialog(self)
        dlg.accounts_changed.connect(self._on_accounts_changed)
        dlg.exec()

    def _on_accounts_changed(self):
        self.load_notebooks()

    def login_notebooklm(self):
        """Quick sign-in for the active account (Chrome cookies)."""
        self.topbar.set_status("Signing in via Chrome...")
        agent.launch_notebooklm_login(agent.get_notebooklm_profile(), browser_cookies=True)
        QMessageBox.information(
            self,
            "NotebookLM sign-in",
            "Sign into Google in Chrome first, then click Refresh.\n"
            "For multiple accounts, use the Account button.",
        )

    def load_reports(self):
        self.report_paths = list(agent.list_report_files())
        self._populate_report_list()

    def on_report_selected(self, row: int):
        item = self.notebook_panel.report_list.item(row)
        if not item:
            return
        idx = item.data(Qt.ItemDataRole.UserRole)
        if idx is None or idx < 0 or idx >= len(self.report_paths):
            return
        self.open_report_file(str(self.report_paths[idx]))

    def refresh_credits(self):
        try:
            if agent.api_key_configured():
                self.context.set_credits_summary(
                    agent.format_credit_meter(), show=False
                )
            else:
                self.context.set_credits_summary("", show=False)
        except Exception:
            self.context.set_credits_summary("", show=False)

    def set_busy(self, busy: bool):
        self.input_bar.send_btn.setDisabled(busy)
        self.input_bar.input.setDisabled(busy)

    def send_question(self):
        if not agent.api_key_configured():
            QMessageBox.warning(
                self,
                "API key",
                "Open Settings and add your OpenRouter key.",
            )
            self.open_settings()
            return

        if not self.notebook_id:
            QMessageBox.warning(
                self,
                "Notebook",
                "No notebook loaded. Open Notebook and pick one, then Refresh.",
            )
            return

        question = self.input_bar.input.text().strip()
        if not question:
            return

        self.input_bar.input.clear()
        self.document.add_user_prompt(question)
        self.document.start_analysis()
        self.set_busy(True)
        self.topbar.set_status("Querying NotebookLM...")
        self.app_sidebar.select_view("chat")

        self.worker = ResearchWorker(question, self.notebook_id)
        self.worker.status.connect(self.on_status)
        self.worker.chunk.connect(self.on_chunk_received)
        self.worker.finished.connect(self.on_research_done)
        self.worker.start()

    def on_status(self, text: str):
        self.topbar.set_status(text)

    def on_chunk_received(self, text: str):
        self.document.append_analysis_chunk(text)

    def on_research_done(self, result: dict):
        self.set_busy(False)

        if not result.get("ok"):
            error = result.get("error", "Unknown error")
            self.document.show_error(f"Error: {error}")
            self.topbar.set_status(f"Error: {error}")
            return

        self.document.finalize_analysis()

        nb_answer = result.get("notebook_answer") or ""
        refs = result.get("references") or []
        ref_count = agent.count_citations(refs, nb_answer)

        self.context.set_sources(nb_answer, refs)
        self.context.set_citations(ref_count)
        self.context.set_synthesis_note(nb_answer)

        path = result.get("report_path")
        if path:
            self.last_report_path = path
            self.load_reports()
            self.topbar.set_status("Done · report saved")
        else:
            self.topbar.set_status("Done")

        self.refresh_credits()
        if self._last_view == "analysis":
            self.refresh_analysis()

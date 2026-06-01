from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QScrollArea,
)

from UI.Widgets.source_card import SourceCard
from UI.source_detail_dialog import SourceDetailDialog


class SourceHubPanel(QWidget):
    """Grid of NotebookLM sources for the active notebook."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("documentPanel")
        self._sources: list = []
        self._notebook_title = ""
        self._search_query = ""

        outer = QVBoxLayout(self)
        outer.setContentsMargins(48, 32, 48, 32)
        outer.setSpacing(16)

        title = QLabel("Source Hub")
        title.setObjectName("documentTitle")
        self.subtitle = QLabel("Select a notebook to load sources.")
        self.subtitle.setObjectName("documentMeta")
        self.subtitle.setWordWrap(True)
        outer.addWidget(title)
        outer.addWidget(self.subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setObjectName("modernScroll")

        self.host = QWidget()
        self.grid = QVBoxLayout(self.host)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(12)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self.host)
        outer.addWidget(scroll, stretch=1)

    def _show_detail(self, card: SourceCard):
        text = card.card_detail or card.card_excerpt or card.card_title
        if card.card_url:
            text = f"{card.card_url}\n\n{text}"
        SourceDetailDialog(card.card_title, text, self).exec()

    def _clear(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _matches_source(self, src: dict) -> bool:
        if not self._search_query:
            return True
        haystack = " ".join(
            str(src.get(key, "") or "")
            for key in ("title", "type", "url", "status")
        ).lower()
        return self._search_query in haystack

    def show_message(self, message: str):
        self._sources = []
        self._clear()
        lbl = QLabel(message)
        lbl.setObjectName("muted")
        lbl.setWordWrap(True)
        self.grid.addWidget(lbl)
        self.subtitle.setText(message)

    def show_loading(self, notebook_title: str):
        self._notebook_title = notebook_title
        self.subtitle.setText(f"Loading sources for {notebook_title}...")
        self.show_message("Loading sources...")

    def load_sources(self, sources: list, notebook_title: str = ""):
        self._sources = sources or []
        self._notebook_title = notebook_title
        self._render_sources()

    def apply_search(self, query: str):
        self._search_query = query.strip().lower()
        if self._sources:
            self._render_sources()

    def _render_sources(self):
        self._clear()
        visible = [s for s in self._sources if self._matches_source(s)]

        if self._notebook_title:
            label = f"{len(visible)} of {len(self._sources)} sources"
            if self._search_query:
                label += f" matching \"{self._search_query}\""
            label += f" in {self._notebook_title}"
            self.subtitle.setText(label)

        if not visible:
            msg = (
                "No sources match your search."
                if self._search_query
                else "This notebook has no sources yet."
            )
            lbl = QLabel(msg)
            lbl.setObjectName("muted")
            lbl.setWordWrap(True)
            self.grid.addWidget(lbl)
            return

        for i, src in enumerate(visible):
            title = src.get("title") or f"Source {i + 1}"
            src_type = src.get("type") or "Research"
            url = src.get("url") or ""
            excerpt = url or src.get("status") or src_type
            tags = [str(src_type).replace("SourceType.", "")]
            if src.get("status"):
                tags.append(str(src.get("status")))
            card = SourceCard(
                i + 1,
                title,
                str(excerpt)[:220],
                tags[:4],
                url=url,
                detail=str(excerpt),
            )
            card.clicked.connect(lambda _idx, c=card: self._show_detail(c))
            self.grid.addWidget(card)

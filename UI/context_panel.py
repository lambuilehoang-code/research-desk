from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QHBoxLayout,
    QSizePolicy,
)

from UI.Widgets.source_card import SourceCard
from UI.source_detail_dialog import SourceDetailDialog


def _parse_reference(ref, index: int) -> tuple[str, str, list[str], str, str]:
    if isinstance(ref, dict):
        title = ref.get("title") or ref.get("name") or f"Source {index + 1}"
        excerpt = (
            ref.get("snippet")
            or ref.get("text")
            or ref.get("url")
            or ref.get("content")
            or ""
        )
        url = ref.get("url") or ""
        tags = ref.get("tags") or ["Research"]
        if isinstance(tags, str):
            tags = [tags]
        detail = str(excerpt or url)
        return title, str(excerpt)[:220], tags[:4], url, detail

    text = str(ref)
    return f"Source {index + 1}", text[:220], ["Research"], "", text


class ContextPanel(QWidget):
    """Right panel — Notebook Reference (Stitch Chat view)."""

    browse_reports_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(280)
        self.setMaximumWidth(340)
        self.setObjectName("contextPanel")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        header_row = QHBoxLayout()
        title = QLabel("Notebook Reference")
        title.setObjectName("panelTitle")
        header_row.addWidget(title)
        header_row.addStretch()
        outer.addLayout(header_row)

        ref_card = QFrame()
        ref_card.setObjectName("panelCard")
        ref_card_layout = QVBoxLayout(ref_card)
        ref_card_layout.setContentsMargins(12, 12, 12, 12)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll.setObjectName("modernScroll")
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.cards_host = QWidget()
        self.cards_host.setMinimumWidth(0)
        self.cards_layout = QVBoxLayout(self.cards_host)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(12)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        placeholder = QLabel("Sources will appear here after you send a question.")
        placeholder.setObjectName("muted")
        placeholder.setWordWrap(True)
        placeholder.setMinimumWidth(0)
        self.cards_layout.addWidget(placeholder)

        self.scroll.setWidget(self.cards_host)
        ref_card_layout.addWidget(self.scroll)
        outer.addWidget(ref_card, stretch=1)

        self.synthesis_card = QFrame()
        self.synthesis_card.setObjectName("synthesisCard")
        syn_layout = QVBoxLayout(self.synthesis_card)
        syn_layout.setContentsMargins(16, 14, 16, 14)
        syn_title = QLabel("Key synthesis note")
        syn_title.setObjectName("sectionTitle")
        self.synthesis_text = QLabel("—")
        self.synthesis_text.setWordWrap(True)
        self.synthesis_text.setMinimumWidth(0)
        self.synthesis_text.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        self.synthesis_text.setObjectName("sourceExcerpt")
        syn_layout.addWidget(syn_title)
        syn_layout.addWidget(self.synthesis_text)
        self.synthesis_card.hide()
        outer.addWidget(self.synthesis_card)

        self.citations_label = QLabel("Citations: 0")
        self.citations_label.setObjectName("statChip")
        outer.addWidget(self.citations_label)

        btn_row = QHBoxLayout()
        self.open_report_btn = QPushButton("Browse reports")
        self.open_report_btn.setObjectName("secondary")
        btn_row.addWidget(self.open_report_btn, stretch=1)
        outer.addLayout(btn_row)

        self.credits_label = QLabel("")
        self.credits_label.setWordWrap(True)
        self.credits_label.setMinimumWidth(0)
        self.credits_label.setObjectName("muted")
        self.credits_label.hide()
        outer.addWidget(self.credits_label)

        self.open_report_btn.clicked.connect(self.browse_reports_requested.emit)

    def _content_width(self) -> int:
        return max(0, self.width() - 32)

    def _sync_wrap_widths(self):
        width = self._content_width()
        if width <= 0:
            return
        viewport_w = self.scroll.viewport().width()
        if viewport_w > 0:
            self.cards_host.setMaximumWidth(viewport_w)
        self.synthesis_text.setMaximumWidth(width - 32)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._sync_wrap_widths()

    def _clear_cards(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _show_reference_detail(self, card: SourceCard):
        text = card.card_detail or card.card_excerpt or card.card_title
        if card.card_url:
            text = f"{card.card_url}\n\n{text}"
        SourceDetailDialog(card.card_title, text, self).exec()

    def clear(self):
        self._clear_cards()
        lbl = QLabel("Sources will appear here after you send a question.")
        lbl.setObjectName("muted")
        lbl.setWordWrap(True)
        lbl.setMinimumWidth(0)
        self.cards_layout.addWidget(lbl)
        self.set_citations(0)
        self.set_synthesis_note("")
        self.synthesis_card.hide()
        self._sync_wrap_widths()

    def set_sources(self, answer: str, references: list | None = None):
        self._clear_cards()
        refs = references or []

        if refs:
            for i, ref in enumerate(refs[:8]):
                title, excerpt, tags, url, detail = _parse_reference(ref, i)
                card = SourceCard(i + 1, title, excerpt, tags, url=url, detail=detail)
                card.clicked.connect(lambda _idx, c=card: self._show_reference_detail(c))
                self.cards_layout.addWidget(card)
        elif answer:
            excerpt = answer if len(answer) <= 220 else answer[:220] + "..."
            card = SourceCard(
                1,
                "NotebookLM synthesis",
                excerpt,
                ["Research"],
                detail=answer,
            )
            card.clicked.connect(lambda _idx, c=card: self._show_reference_detail(c))
            self.cards_layout.addWidget(card)
        else:
            lbl = QLabel("No sources yet.")
            lbl.setObjectName("muted")
            lbl.setWordWrap(True)
            lbl.setMinimumWidth(0)
            self.cards_layout.addWidget(lbl)

        self._sync_wrap_widths()

    def set_synthesis_note(self, text: str):
        if text and text.strip():
            preview = text if len(text) <= 280 else text[:280] + "..."
            self.synthesis_text.setText(preview)
            self.synthesis_card.show()
            self._sync_wrap_widths()
        else:
            self.synthesis_card.hide()

    def set_citations(self, count: int):
        self.citations_label.setText(f"Citations: {count}")
        self.citations_label.show()

    def set_credits_summary(self, text: str, show: bool = False):
        if show and text.strip():
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            short = " · ".join(lines[:3]) if lines else text[:120]
            self.credits_label.setText(short)
            self.credits_label.show()
            self._sync_wrap_widths()
        else:
            self.credits_label.hide()

    def show_report_sources(self, markdown_text: str):
        import research_agent as agent

        excerpt = markdown_text
        if "## NotebookLM Research" in markdown_text:
            part = markdown_text.split("## NotebookLM Research", 1)[1]
            if "##" in part:
                part = part.split("##", 1)[0]
            excerpt = part.strip()
        self.set_sources(excerpt, None)
        self.set_citations(agent.count_citations_in_report(markdown_text))
        self.set_synthesis_note("")

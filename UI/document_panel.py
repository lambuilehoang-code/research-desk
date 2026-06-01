import re
import markdown
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QLabel,
    QFrame,
)


def _markdown_html(text: str) -> str:
    html = markdown.markdown(text, extensions=["extra", "nl2br"])
    return (
        '<div style="color:#000000;font-family:Georgia,\'Times New Roman\',serif;'
        'font-size:11.5pt;line-height:1.4;">'
        f"{html}</div>"
    )


def _report_title(md: str) -> str:
    if "## Question" in md:
        q = md.split("## Question", 1)[1].strip().split("\n", 1)[0].strip()
        if q:
            return q[:120]
    return "Research Synthesis"


def _report_date(md: str) -> str:
    m = re.search(r"\*\*Generated:\*\*\s*(.+)", md)
    if m:
        return m.group(1).strip()[:19]
    return ""


class DocumentPanel(QWidget):
    """Center document panel — Stitch Chat / Notebook editor style."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("documentPanel")
        self._analysis_label: QLabel | None = None
        self._analysis_raw = ""

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll.setObjectName("modernScroll")

        self.host = QWidget()
        self.layout = QVBoxLayout(self.host)
        self.layout.setContentsMargins(48, 32, 48, 32)
        self.layout.setSpacing(16)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.title = QLabel("Research Synthesis")
        self.title.setObjectName("documentTitle")
        self.title.setWordWrap(True)

        self.subtitle = QLabel("Select a notebook and ask a question to begin.")
        self.subtitle.setObjectName("documentMeta")
        self.subtitle.setWordWrap(True)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.subtitle)
        self.layout.addStretch()

        self.scroll.setWidget(self.host)
        outer.addWidget(self.scroll)

    def set_notebook(self, title: str):
        self.title.setText(title or "Research Synthesis")
        self.subtitle.setText(
            "Ask a question below to synthesize sources from this notebook."
        )

    def _insert_before_stretch(self, widget: QWidget):
        self.layout.insertWidget(self.layout.count() - 1, widget)

    def add_user_prompt(self, text: str):
        card = QFrame()
        card.setObjectName("promptCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)

        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setObjectName("promptText")
        card_layout.addWidget(lbl)
        self._insert_before_stretch(card)

    def start_analysis(self):
        heading = QLabel("Analysis")
        heading.setObjectName("sectionHeading")
        self._insert_before_stretch(heading)

        self._analysis_raw = ""
        self._analysis_label = QLabel("")
        self._analysis_label.setWordWrap(True)
        self._analysis_label.setObjectName("documentBody")
        self._analysis_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._insert_before_stretch(self._analysis_label)

    def append_analysis_chunk(self, chunk: str):
        if not self._analysis_label:
            return
        self._analysis_raw += chunk
        self._analysis_label.setText(self._analysis_raw)
        self._scroll_to_bottom()

    def finalize_analysis(self):
        if not self._analysis_label or not self._analysis_raw.strip():
            return
        self._analysis_label.setTextFormat(Qt.TextFormat.RichText)
        self._analysis_label.setText(_markdown_html(self._analysis_raw))
        self._scroll_to_bottom()

    def _clear_document(self):
        """Remove dynamic content only; keep title and subtitle widgets alive."""
        self._analysis_label = None
        self._analysis_raw = ""
        while self.layout.count() > 3:
            item = self.layout.takeAt(2)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def reset_welcome(self):
        self._clear_document()
        self.title.setText("Research Synthesis")
        self.subtitle.setText("Select a notebook and ask a question to begin.")

    def show_error(self, message: str):
        self.subtitle.setText(message)

    def show_report(self, markdown_text: str):
        self._clear_document()

        self.title.setText(_report_title(markdown_text))
        date_str = _report_date(markdown_text)
        self.subtitle.setText(date_str if date_str else "Saved report")

        body = QLabel()
        body.setWordWrap(True)
        body.setObjectName("documentBody")
        body.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        body.setTextFormat(Qt.TextFormat.RichText)
        preview = (
            markdown_text
            if len(markdown_text) <= 12000
            else markdown_text[:12000] + "\n\n..."
        )
        body.setText(_markdown_html(preview))

        self._insert_before_stretch(body)

    def _scroll_to_bottom(self):
        bar = self.scroll.verticalScrollBar()
        bar.setValue(bar.maximum())

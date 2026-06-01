from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QStyle

_NAV_PIXMAPS: dict[str, QStyle.StandardPixmap] = {
    "sources": QStyle.StandardPixmap.SP_DirIcon,
    "chat": QStyle.StandardPixmap.SP_MessageBoxInformation,
    "analysis": QStyle.StandardPixmap.SP_FileDialogDetailedView,
    "notebook": QStyle.StandardPixmap.SP_FileIcon,
    "settings": QStyle.StandardPixmap.SP_FileDialogContentsView,
}


def nav_icon(view_id: str) -> QIcon:
    app = QApplication.instance()
    if app is None:
        return QIcon()
    pixmap = _NAV_PIXMAPS.get(view_id, QStyle.StandardPixmap.SP_FileIcon)
    return app.style().standardIcon(pixmap)

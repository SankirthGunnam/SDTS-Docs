#!/usr/bin/env python3
"""
SDTS Documentation Viewer – a simple Qt browser that displays static HTML
from the static-docs folder. No localhost or server; loads files directly.
"""

import sys
from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile

# Base directory for static docs (next to this script)
STATIC_DOCS = Path(__file__).resolve().parent / "static-docs"
# Entry point: hierarchical build uses 1-rf-board-bring-up/home.html
HOME_PAGE_CANDIDATES = ("1-rf-board-bring-up/home.html", "home.html")


class DocWebEnginePage(QWebEnginePage):
    """Allow navigation only within static-docs (local files)."""

    def __init__(self, base_dir: Path, profile: QWebEngineProfile, parent=None):
        super().__init__(profile, parent)
        self._base_dir = base_dir.resolve()

    def acceptNavigationRequest(self, url: QUrl, nav_type, is_main_frame: bool) -> bool:
        if not is_main_frame:
            return True
        if url.scheme() == "file":
            path = Path(url.toLocalFile())
            try:
                path = path.resolve()
                path.relative_to(self._base_dir)
            except (ValueError, OSError):
                return False
        elif url.scheme() in ("http", "https"):
            return False
        return True


class DocViewerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SDTS Documentation")
        self.resize(1200, 800)

        profile = QWebEngineProfile.defaultProfile()
        page = DocWebEnginePage(STATIC_DOCS, profile, self)
        self._view = QWebEngineView(self)
        self._view.setPage(page)
        self.setCentralWidget(self._view)

        home_path = None
        for rel in HOME_PAGE_CANDIDATES:
            p = STATIC_DOCS / rel
            if p.exists():
                home_path = p
                break
        if home_path is not None:
            url = QUrl.fromLocalFile(str(home_path.resolve()))
            self._view.setUrl(url)
        else:
            self._view.setHtml(
                "<p>No home page found in static-docs.</p>"
                "<p>Run: <code>python build_docs.py docs -o static-docs</code></p>"
            )


def main():
    if not STATIC_DOCS.is_dir():
        print(f"Error: static-docs folder not found: {STATIC_DOCS}", file=sys.stderr)
        print("Run: python build_docs.py docs -o static-docs", file=sys.stderr)
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("SDTS Documentation Viewer")
    window = DocViewerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

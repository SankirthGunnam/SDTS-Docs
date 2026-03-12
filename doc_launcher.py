#!/usr/bin/env python3
"""
PyQt app with a central QTextEdit showing sample text with hyperlinks to the docs.
Clicking a link opens the HTML page in a bottom dock widget (in-app), not the browser.
"""

import sys
from pathlib import Path

from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QDockWidget, QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile

STATIC_DOCS = Path(__file__).resolve().parent / "static-docs"


class DocWebEnginePage(QWebEnginePage):
    """Only allow navigation within static-docs (local files)."""

    def __init__(self, base_dir: Path, profile: QWebEngineProfile, parent=None):
        super().__init__(profile, parent)
        self._base_dir = base_dir.resolve()

    def acceptNavigationRequest(self, url: QUrl, nav_type, is_main_frame: bool) -> bool:
        if not is_main_frame:
            return True
        if url.scheme() == "file":
            path = Path(url.toLocalFile())
            try:
                path.resolve().relative_to(self._base_dir)
            except (ValueError, OSError):
                return False
        elif url.scheme() in ("http", "https"):
            return False
        return True


class LinkableTextEdit(QTextEdit):
    """QTextEdit that handles link clicks via anchorAt() (PyQt6 has no anchorClicked)."""

    def __init__(self, on_link_clicked=None, parent=None):
        super().__init__(parent)
        self._on_link_clicked = on_link_clicked
        self._pressed_anchor = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed_anchor = self.anchorAt(event.position().toPoint())
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._pressed_anchor:
            anchor = self.anchorAt(event.position().toPoint())
            if anchor == self._pressed_anchor and self._on_link_clicked:
                self._on_link_clicked(anchor)
            self._pressed_anchor = None
        super().mouseReleaseEvent(event)

SAMPLE_TEXT = """<h2>SDTS Documentation Launcher</h2>
<p>This window shows content with links to the generated documentation. 
Click any link to open that page in the bottom panel.</p>

<h3>Getting started</h3>
<p>Start from the <a href="home.html">Home</a> page for an overview of the SDTS documentation. 
From there you can follow the <a href="build.html">Build</a> guide to compile and run the tools, 
and adjust <a href="settings.html">Settings</a> for your environment. 
The <a href="home.html">Home</a> page also describes the main sections: board bring-up, 
configuration, and test assurance.</p>

<h3>Board and configuration</h3>
<p>For RF board bring-up, use <a href="band-management.html">Band Management</a> to configure 
supported bands, then set up <a href="device-setting.html">Device Setting</a> and 
<a href="band-config.html">Band Config</a> as needed. Calibration is covered in 
<a href="cal-path-info.html">Cal Path Info</a>. 
RFFE and register setup are in <a href="rffe-config.html">RFFE Config</a> and 
<a href="reg-config.html">Regy Config</a>.</p>

<h3>Test assurance process</h3>
<p>Test flows include <a href="search-simulation.html">Search Simulation</a> for finding 
and simulating scenarios, <a href="test-checker-data.html">Test Checker Data</a> for 
validating test data, and <a href="bcf-verification.html">BCF Verification</a> for BCF checks. 
You can also use <a href="mipi-extractor.html">MIPI Extractor</a> and 
<a href="dr-simulation.html">DR Simulation</a> for MIPI and DR workflows. 
Refer to <a href="build.html">Build</a> for how to run these from the command line.</p>

<h3>Laboratory and tools</h3>
<p>For lab use and tooling, see <a href="laboratory.html">Laboratory</a> for procedures 
and <a href="eutg.html">EUTG</a> for EUTG-related features. 
Reserved sections are linked here: <a href="section2.html">Section 2</a> and 
<a href="section3.html">Section 3</a>.</p>

<p><strong>Quick links:</strong> <a href="home.html">Home</a> · 
<a href="build.html">Build</a> · <a href="settings.html">Settings</a> · 
<a href="band-management.html">Band Management</a> · 
<a href="laboratory.html">Laboratory</a> · <a href="eutg.html">EUTG</a></p>
"""


class DocLauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SDTS Documentation Launcher")
        self.resize(800, 640)

        self._text_edit = LinkableTextEdit(on_link_clicked=self._on_link_clicked, parent=self)
        self._text_edit.setReadOnly(True)
        self._text_edit.setAcceptRichText(True)
        self._text_edit.setHtml(SAMPLE_TEXT)
        self.setCentralWidget(self._text_edit)

        # Bottom dock: web view for opened doc pages
        self._doc_view = QWebEngineView(self)
        profile = QWebEngineProfile.defaultProfile()
        page = DocWebEnginePage(STATIC_DOCS, profile, self)
        self._doc_view.setPage(page)
        dock = QDockWidget("Documentation", self)
        dock.setObjectName("DocDock")
        dock.setWidget(self._doc_view)
        dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)
        # Start with dock visible but empty; first link click will load a page

    def _on_link_clicked(self, href: str):
        path = (href or "").strip() or "home.html"
        name = path.split("/")[-1].split("?")[0]
        if not name.endswith(".html"):
            name = name + ".html" if name else "home.html"
        file_path = next(STATIC_DOCS.rglob(name), None)
        if file_path is not None and file_path.is_file():
            url = QUrl.fromLocalFile(str(file_path.resolve()))
            self._doc_view.setUrl(url)


def main():
    if not STATIC_DOCS.is_dir():
        print(f"Error: static-docs not found: {STATIC_DOCS}", file=sys.stderr)
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("SDTS Doc Launcher")
    window = DocLauncherWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

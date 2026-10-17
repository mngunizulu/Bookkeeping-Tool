from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication
from .db import Database, default_paths
from .ui import MainWindow, APP_STYLE
from .i18n import tr


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Asart Bookkeeping")
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLE)
    paths = default_paths()
    db = Database(paths.database)
    win = MainWindow(db, paths)
    company = db.get_company()
    win.setWindowTitle(f"{company['company_name']} – {tr('app_title', db.get_language())}")
    win.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())

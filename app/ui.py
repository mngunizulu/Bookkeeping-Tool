from __future__ import annotations

import os
import sys
import tempfile
from datetime import date
from pathlib import Path

from PySide6.QtCore import QDate, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QFont, QImage, QPalette, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QCheckBox, QComboBox, QDateEdit, QDialog,
    QDialogButtonBox, QFileDialog, QFormLayout, QFrame, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow,
    QMessageBox, QPushButton, QScrollArea, QSpinBox, QDoubleSpinBox, QStackedWidget,
    QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget
)

from .backup import create_backup
from .db import AppPaths, Database
from .documents import archive_document
from .reports import euro, export_csv, export_excel, export_pdf
from .i18n import LANGUAGES, category_label, document_type_label, kind_label, payment_label, tr


APP_STYLE = """
QMainWindow, QDialog {
    background: #f5f7fb;
    color: #172033;
}

QWidget {
    font-family: 'Segoe UI';
    font-size: 10.5pt;
    color: #172033;
}

QLabel, QCheckBox, QRadioButton {
    color: #172033;
}

QFrame#sidebar {
    background: #172033;
    border: none;
}

QLabel#brand {
    color: white;
    font-size: 18pt;
    font-weight: 700;
    padding: 4px 8px;
}

QLabel#brandSub {
    color: #aeb8ca;
    font-size: 9pt;
    padding: 0 8px 14px 8px;
}

QListWidget#nav {
    background: transparent;
    border: none;
    color: #cbd3e2;
    outline: none;
}

QListWidget#nav::item {
    color: #cbd3e2;
    padding: 11px 14px;
    margin: 2px 6px;
    border-radius: 8px;
}

QListWidget#nav::item:selected {
    background: #2f6fed;
    color: white;
    font-weight: 600;
}

QListWidget#nav::item:hover {
    background: #243149;
    color: white;
}

QFrame.card {
    background: white;
    border: 1px solid #e2e7f0;
    border-radius: 12px;
}

QLabel.cardTitle {
    color: #667085;
    font-size: 9.5pt;
}

QLabel.cardValue {
    color: #172033;
    font-size: 22pt;
    font-weight: 700;
}

QLabel.pageTitle {
    color: #172033;
    font-size: 22pt;
    font-weight: 700;
}

QLabel.pageSub {
    color: #667085;
}

QPushButton {
    min-height: 34px;
    padding: 0 14px;
    border-radius: 7px;
    border: 1px solid #ccd4e0;
    background: white;
    color: #172033;
}

QPushButton:hover {
    background: #f0f4fa;
}

QPushButton:disabled {
    color: #98a2b3;
    background: #f2f4f7;
    border-color: #e4e7ec;
}

QPushButton#primary {
    background: #2f6fed;
    color: white;
    border: 1px solid #2f6fed;
    font-weight: 600;
}

QPushButton#primary:hover {
    background: #245fd0;
}

QPushButton#danger {
    color: #b42318;
    border-color: #f3c7c4;
    background: #fffafa;
}

QLineEdit,
QComboBox,
QDateEdit,
QDoubleSpinBox,
QSpinBox,
QTextEdit {
    min-height: 34px;
    color: #172033;
    background-color: #ffffff;
    border: 1px solid #cfd6e4;
    border-radius: 7px;
    padding: 0 8px;
    selection-background-color: #2f6fed;
    selection-color: #ffffff;
}

QTextEdit {
    padding: 8px;
}

QLineEdit::placeholder {
    color: #98a2b3;
}

QLineEdit:focus,
QComboBox:focus,
QDateEdit:focus,
QDoubleSpinBox:focus,
QSpinBox:focus,
QTextEdit:focus {
    border: 1px solid #2f6fed;
}

QLineEdit:read-only,
QDateEdit:read-only,
QDoubleSpinBox:read-only,
QSpinBox:read-only,
QTextEdit:read-only {
    color: #344054;
    background-color: #f8fafc;
}

QLineEdit:disabled,
QComboBox:disabled,
QDateEdit:disabled,
QDoubleSpinBox:disabled,
QSpinBox:disabled,
QTextEdit:disabled,
QCheckBox:disabled {
    color: #98a2b3;
    background-color: #f2f4f7;
}

QComboBox QAbstractItemView {
    color: #172033;
    background-color: #ffffff;
    border: 1px solid #cfd6e4;
    selection-background-color: #2f6fed;
    selection-color: #ffffff;
    outline: none;
}

QComboBox QAbstractItemView::item {
    min-height: 30px;
    padding: 4px 8px;
}

QComboBox {
    color: #172033;
    background-color: #ffffff;
}

QCalendarWidget QWidget {
    color: #172033;
    background-color: #ffffff;
}

QCalendarWidget QAbstractItemView:enabled {
    color: #172033;
    background-color: #ffffff;
    selection-background-color: #2f6fed;
    selection-color: #ffffff;
}

QTableWidget {
    color: #172033;
    background: white;
    border: 1px solid #e2e7f0;
    border-radius: 8px;
    gridline-color: #edf0f5;
    alternate-background-color: #fafbfc;
}

QHeaderView::section {
    background: #f7f9fc;
    color: #475467;
    font-weight: 600;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #e2e7f0;
}

QTableWidget::item {
    color: #172033;
    padding: 6px;
}

QTableWidget::item:selected {
    background: #dfe9ff;
    color: #172033;
}

QMenuBar, QMenu {
    color: #172033;
    background-color: #ffffff;
}

QMenu::item:selected {
    color: #172033;
    background-color: #dfe9ff;
}

QFrame#taskBox {
    background: #fff8e7;
    border: 1px solid #f1d58a;
    border-radius: 10px;
}

QLabel#taskCount {
    color: #9a6500;
    font-size: 20pt;
    font-weight: 700;
}

QLabel#muted {
    color: #667085;
}

QLabel#statusGood {
    color: #027a48;
    font-weight: 600;
}

QLabel#statusWarn {
    color: #b54708;
    font-weight: 600;
}
"""


def qdate_to_iso(qd: QDate) -> str:
    return f"{qd.year():04d}-{qd.month():02d}-{qd.day():02d}"


def cents(value: float) -> int:
    return int(round(value * 100))


def open_path(path: str | Path):
    p = str(path)
    if sys.platform.startswith("win"):
        os.startfile(p)
    elif sys.platform == "darwin":
        os.system(f'open "{p}"')
    else:
        os.system(f'xdg-open "{p}"')


def ask_yes_no(parent, title: str, text: str, language: str) -> bool:
    box = QMessageBox(QMessageBox.Question, title, text, QMessageBox.Yes | QMessageBox.No, parent)
    box.button(QMessageBox.Yes).setText(tr("yes", language))
    box.button(QMessageBox.No).setText(tr("no", language))
    box.setDefaultButton(QMessageBox.No)
    return box.exec() == QMessageBox.Yes


def make_page_header(title: str, subtitle: str) -> tuple[QWidget, QHBoxLayout]:
    w = QWidget()
    row = QHBoxLayout(w)
    row.setContentsMargins(0, 0, 0, 0)
    text = QVBoxLayout()
    t = QLabel(title); t.setProperty("class", "pageTitle")
    s = QLabel(subtitle); s.setProperty("class", "pageSub"); s.setWordWrap(True)
    text.addWidget(t); text.addWidget(s)
    row.addLayout(text, 1)
    return w, row


class KpiCard(QFrame):
    def __init__(self, title: str):
        super().__init__()
        self.setProperty("class", "card")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 15, 18, 15)
        title_lbl = QLabel(title); title_lbl.setProperty("class", "cardTitle")
        self.value = QLabel("0,00 €"); self.value.setProperty("class", "cardValue")
        self.detail = QLabel(""); self.detail.setObjectName("muted")
        lay.addWidget(title_lbl); lay.addWidget(self.value); lay.addWidget(self.detail)


class CameraDialog(QDialog):
    def __init__(self, parent=None, language: str = "en"):
        super().__init__(parent)
        self.language = language
        self.setWindowTitle(tr("capture_document", language))
        self.resize(900, 680)
        self.capture = None
        self.frame = None
        self.saved_path: Path | None = None
        self.preview = QLabel(tr("opening_camera", language))
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumSize(680, 500)
        self.preview.setStyleSheet("background:#101828;color:#fff;border-radius:10px;")
        self.btn_capture = QPushButton(tr("capture_photo", language)); self.btn_capture.setObjectName("primary")
        self.btn_capture.clicked.connect(self.take_photo)
        self.btn_cancel = QPushButton(tr("cancel", language)); self.btn_cancel.clicked.connect(self.reject)
        row = QHBoxLayout(); row.addStretch(); row.addWidget(self.btn_cancel); row.addWidget(self.btn_capture)
        lay = QVBoxLayout(self); lay.addWidget(self.preview, 1); lay.addLayout(row)
        self.timer = QTimer(self); self.timer.timeout.connect(self._next_frame)
        try:
            import cv2
            self.cv2 = cv2
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                raise RuntimeError(tr("no_camera", language))
            self.timer.start(40)
        except Exception as exc:
            self.preview.setText(tr("camera_unavailable", language, error=exc))
            self.btn_capture.setEnabled(False)

    def _next_frame(self):
        if self.capture is None:
            return
        ok, frame = self.capture.read()
        if not ok:
            return
        self.frame = frame
        rgb = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888).copy()
        self.preview.setPixmap(QPixmap.fromImage(img).scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def take_photo(self):
        if self.frame is None:
            return
        fd, filename = tempfile.mkstemp(prefix="bookkeeping_receipt_", suffix=".jpg")
        os.close(fd)
        self.cv2.imwrite(filename, self.frame)
        self.saved_path = Path(filename)
        self.accept()

    def closeEvent(self, event):
        self._cleanup(); super().closeEvent(event)

    def accept(self):
        self._cleanup(); super().accept()

    def reject(self):
        self._cleanup(); super().reject()

    def _cleanup(self):
        self.timer.stop()
        if self.capture is not None:
            self.capture.release(); self.capture = None


class TransactionDialog(QDialog):
    def __init__(self, db: Database, paths: AppPaths, kind: str = "expense", tx_id: int | None = None,
                 preset_document_ids: list[int] | None = None, parent=None):
        super().__init__(parent)
        self.db, self.paths, self.tx_id = db, paths, tx_id
        self.language = db.get_language()
        self.document_ids: list[int] = list(preset_document_ids or [])
        self.setWindowTitle(tr("book_expense", self.language) if kind == "expense" else tr("book_income", self.language))
        self.resize(760, 760)

        title = QLabel(tr("book_transaction", self.language)); title.setProperty("class", "pageTitle")
        subtitle = QLabel(tr("book_transaction_sub", self.language))
        subtitle.setProperty("class", "pageSub"); subtitle.setWordWrap(True)

        self.kind = QComboBox(); self.kind.addItem(tr("expense", self.language), "expense"); self.kind.addItem(tr("income", self.language), "income"); self.kind.setCurrentIndex(max(0, self.kind.findData(kind)))
        self.booking_date = QDateEdit(QDate.currentDate()); self.booking_date.setCalendarPopup(True); self.booking_date.setDisplayFormat("dd.MM.yyyy")
        self.document_date = QDateEdit(QDate.currentDate()); self.document_date.setCalendarPopup(True); self.document_date.setDisplayFormat("dd.MM.yyyy")
        self.counterparty = QLineEdit(); self.counterparty.setPlaceholderText(tr("supplier_customer_placeholder", self.language))
        self.category = QComboBox()
        self.description = QLineEdit(); self.description.setPlaceholderText(tr("description_placeholder", self.language))
        self.document_number = QLineEdit(); self.document_number.setPlaceholderText(tr("invoice_receipt_placeholder", self.language))
        self.gross = QDoubleSpinBox(); self.gross.setRange(0, 999999999); self.gross.setDecimals(2); self.gross.setSuffix(" €")
        self.vat_rate = QComboBox(); self.vat_rate.addItems(["0", "7", "19"]); self.vat_rate.setCurrentText("19")
        self.net = QDoubleSpinBox(); self.net.setRange(0, 999999999); self.net.setDecimals(2); self.net.setSuffix(" €"); self.net.setReadOnly(True)
        self.vat = QDoubleSpinBox(); self.vat.setRange(0, 999999999); self.vat.setDecimals(2); self.vat.setSuffix(" €"); self.vat.setReadOnly(True)
        self.payment = QComboBox();
        for value in ["Bank", "Card", "Cash", "PayPal", "Other"]: self.payment.addItem(payment_label(value, self.language), value)
        self.paid = QCheckBox(tr("paid_received", self.language)); self.paid.setChecked(True)
        self.deductible = QDoubleSpinBox(); self.deductible.setRange(0, 100); self.deductible.setDecimals(0); self.deductible.setValue(100); self.deductible.setSuffix(" %")
        self.notes = QTextEdit(); self.notes.setMaximumHeight(90)
        self.docs_label = QLabel(); self.docs_label.setObjectName("muted")
        self._update_docs_label()

        self.btn_attach = QPushButton(tr("upload_document", self.language))
        self.btn_camera = QPushButton(tr("capture_photo", self.language))
        self.btn_attach.clicked.connect(self.attach_document); self.btn_camera.clicked.connect(self.take_photo)
        self.kind.currentIndexChanged.connect(self.reload_categories)
        self.gross.valueChanged.connect(self.recalc); self.vat_rate.currentTextChanged.connect(self.recalc)

        form_frame = QFrame(); form_frame.setProperty("class", "card")
        form = QFormLayout(form_frame); form.setContentsMargins(22, 20, 22, 20); form.setSpacing(12)
        form.addRow(tr("type", self.language), self.kind); form.addRow(tr("booking_date", self.language), self.booking_date); form.addRow(tr("invoice_date", self.language), self.document_date)
        form.addRow(tr("supplier_customer", self.language), self.counterparty); form.addRow(tr("category", self.language), self.category)
        form.addRow(tr("description", self.language) + " *", self.description); form.addRow(tr("invoice_receipt_no", self.language), self.document_number)
        form.addRow(tr("gross_amount", self.language) + " *", self.gross); form.addRow(tr("vat_rate", self.language), self.vat_rate); form.addRow(tr("net_amount", self.language), self.net); form.addRow(tr("vat", self.language), self.vat)
        form.addRow(tr("payment_method", self.language), self.payment); form.addRow("", self.paid); form.addRow(tr("tax_deductible", self.language), self.deductible); form.addRow(tr("notes", self.language), self.notes)

        docs_frame = QFrame(); docs_frame.setProperty("class", "card")
        docs_lay = QVBoxLayout(docs_frame); docs_lay.setContentsMargins(18, 14, 18, 14)
        docs_title = QLabel(tr("supporting_documents", self.language)); docs_title.setStyleSheet("font-weight:600;")
        docs_buttons = QHBoxLayout(); docs_buttons.addWidget(self.btn_attach); docs_buttons.addWidget(self.btn_camera); docs_buttons.addStretch()
        docs_lay.addWidget(docs_title); docs_lay.addWidget(self.docs_label); docs_lay.addLayout(docs_buttons)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        save_btn = buttons.button(QDialogButtonBox.Save); save_btn.setText(tr("save_transaction", self.language)); save_btn.setObjectName("primary")
        buttons.button(QDialogButtonBox.Cancel).setText(tr("cancel", self.language))
        buttons.accepted.connect(self.save); buttons.rejected.connect(self.reject)

        lay = QVBoxLayout(self); lay.setContentsMargins(22, 20, 22, 20); lay.setSpacing(14)
        lay.addWidget(title); lay.addWidget(subtitle); lay.addWidget(form_frame); lay.addWidget(docs_frame); lay.addWidget(buttons)

        self.reload_categories()
        if tx_id is not None:
            self.load_existing(tx_id)
        self.recalc()

    def _update_docs_label(self):
        n = len(self.document_ids)
        self.docs_label.setText(tr("no_document_attached", self.language) if not n else tr("documents_attached", self.language, count=n))

    def reload_categories(self):
        current = self.category.currentData()
        self.category.clear()
        for c in self.db.list_categories(self.kind.currentData()):
            self.category.addItem(category_label(c["name"], self.language), c["id"])
        if current:
            idx = self.category.findData(current)
            if idx >= 0:
                self.category.setCurrentIndex(idx)

    def recalc(self):
        gross = self.gross.value(); rate = float(self.vat_rate.currentText())
        if rate <= 0:
            net, vat = gross, 0
        else:
            net = gross / (1 + rate / 100.0); vat = gross - net
        self.net.setValue(round(net, 2)); self.vat.setValue(round(vat, 2))

    def attach_document(self):
        files, _ = QFileDialog.getOpenFileNames(self, tr("attach_documents", self.language), "", tr("documents_filter", self.language))
        for file in files:
            try:
                self.document_ids.append(archive_document(self.db, self.paths, Path(file), "receipt"))
            except Exception as exc:
                QMessageBox.critical(self, tr("could_not_archive", self.language), str(exc))
        self._update_docs_label()

    def take_photo(self):
        dlg = CameraDialog(self, self.language)
        if dlg.exec() == QDialog.Accepted and dlg.saved_path:
            try:
                self.document_ids.append(archive_document(self.db, self.paths, dlg.saved_path, "receipt_photo"))
                self._update_docs_label()
            finally:
                try: dlg.saved_path.unlink(missing_ok=True)
                except Exception: pass

    def load_existing(self, tid: int):
        tx = self.db.get_transaction(tid)
        if not tx:
            return
        self.kind.setCurrentIndex(max(0, self.kind.findData(tx["kind"]))); self.reload_categories()
        for widget, val in ((self.booking_date, tx["booking_date"]), (self.document_date, tx["document_date"] or tx["booking_date"])):
            y, m, d = map(int, val.split("-")); widget.setDate(QDate(y, m, d))
        docs = self.db.documents_for_transaction(tid); self.document_ids = [d["id"] for d in docs]
        cp = ""
        with self.db.connect() as con:
            if tx.get("counterparty_id"):
                row = con.execute("SELECT name FROM counterparties WHERE id=?", (tx["counterparty_id"],)).fetchone(); cp = row[0] if row else ""
        self.counterparty.setText(cp)
        idx = self.category.findData(tx["category_id"]); self.category.setCurrentIndex(max(0, idx))
        self.description.setText(tx["description"]); self.document_number.setText(tx.get("document_number") or "")
        self.gross.setValue(tx["gross_amount_cents"] / 100)
        self.vat_rate.setCurrentText(str(int(tx["vat_rate"])) if float(tx["vat_rate"]).is_integer() else str(tx["vat_rate"]))
        self.payment.setCurrentIndex(max(0, self.payment.findData(tx.get("payment_method") or "Bank"))); self.paid.setChecked(bool(tx["paid"])); self.deductible.setValue(tx.get("tax_deductible_percent") or 100)
        self.notes.setPlainText(tx.get("notes") or ""); self._update_docs_label()

    def save(self):
        if not self.description.text().strip() or self.gross.value() <= 0:
            QMessageBox.warning(self, tr("missing_information", self.language), tr("missing_information_msg", self.language))
            return
        kind = self.kind.currentData()
        cp_id = self.db.get_or_create_counterparty(self.counterparty.text(), "supplier" if kind == "expense" else "customer")
        tx = {
            "booking_date": qdate_to_iso(self.booking_date.date()), "document_date": qdate_to_iso(self.document_date.date()),
            "kind": kind, "counterparty_id": cp_id, "category_id": self.category.currentData(), "description": self.description.text().strip(),
            "document_number": self.document_number.text().strip(), "net_amount_cents": cents(self.net.value()), "vat_rate": float(self.vat_rate.currentText()),
            "vat_amount_cents": cents(self.vat.value()), "gross_amount_cents": cents(self.gross.value()), "payment_method": self.payment.currentData(),
            "paid": 1 if self.paid.isChecked() else 0, "tax_deductible_percent": self.deductible.value(), "notes": self.notes.toPlainText().strip(),
        }
        try:
            if self.tx_id is None:
                self.db.add_transaction(tx, self.document_ids)
            else:
                self.db.update_transaction(self.tx_id, tx, self.document_ids)
        except Exception as exc:
            QMessageBox.critical(self, tr("could_not_save", self.language), str(exc)); return
        self.accept()


class SettingsDialog(QDialog):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        c = db.get_company()
        self.language = c.get("language") or "en"
        self.setWindowTitle(tr("company_settings", self.language))
        self.resize(620, 650)

        title = QLabel(tr("company_settings", self.language)); title.setProperty("class", "pageTitle")
        self.company = QLineEdit(c["company_name"]); self.owner = QLineEdit(c["owner_name"]); self.street = QLineEdit(c["street"])
        self.postal = QLineEdit(c["postal_code"]); self.city = QLineEdit(c["city"]); self.tax = QLineEdit(c["tax_number"]); self.vatid = QLineEdit(c["vat_id"]); self.iban = QLineEdit(c["iban"])
        self.klein = QCheckBox(tr("kleinunternehmer", self.language)); self.klein.setChecked(bool(c["kleinunternehmer"]))
        self.fiscal = QSpinBox(); self.fiscal.setRange(1, 12); self.fiscal.setValue(c["fiscal_year_start_month"])
        self.language_combo = QComboBox()
        for code, label in LANGUAGES.items(): self.language_combo.addItem(label, code)
        self.language_combo.setCurrentIndex(max(0, self.language_combo.findData(self.language)))

        card = QFrame(); card.setProperty("class", "card")
        form = QFormLayout(card); form.setContentsMargins(22,20,22,20); form.setSpacing(12)
        for label, w in [
            (tr("company_name",self.language),self.company), (tr("owner",self.language),self.owner),
            (tr("street",self.language),self.street), (tr("postal_code",self.language),self.postal),
            (tr("city",self.language),self.city), (tr("tax_number",self.language),self.tax),
            (tr("vat_id",self.language),self.vatid), (tr("iban",self.language),self.iban),
            (tr("fiscal_year_start",self.language),self.fiscal), (tr("language",self.language),self.language_combo),
        ]: form.addRow(label,w)
        form.addRow("", self.klein)
        note = QLabel(tr("tax_note", self.language)); note.setWordWrap(True); note.setObjectName("muted")
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save); buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.Save).setText(tr("save",self.language)); buttons.button(QDialogButtonBox.Save).setObjectName("primary")
        buttons.button(QDialogButtonBox.Cancel).setText(tr("cancel",self.language))
        lay = QVBoxLayout(self); lay.setContentsMargins(22,20,22,20); lay.addWidget(title); lay.addWidget(card); lay.addWidget(note); lay.addStretch(); lay.addWidget(buttons)

    def save(self):
        self.db.save_company({
            "company_name": self.company.text().strip() or "My Business",
            "owner_name": self.owner.text().strip(), "street": self.street.text().strip(),
            "postal_code": self.postal.text().strip(), "city": self.city.text().strip(),
            "tax_number": self.tax.text().strip(), "vat_id": self.vatid.text().strip(),
            "iban": self.iban.text().strip(), "kleinunternehmer": 1 if self.klein.isChecked() else 0,
            "fiscal_year_start_month": self.fiscal.value(), "language": self.language_combo.currentData(),
        })
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self, db: Database, paths: AppPaths):
        super().__init__()
        self.db, self.paths = db, paths
        self.language = db.get_language()
        self.setWindowTitle(f"{db.get_company()['company_name']} – {tr('app_title', self.language)}")
        self.resize(1440, 900)
        self.setMinimumSize(1100, 720)
        self._build_shell()
        self._build_menu()
        self.refresh_all()

    def _build_shell(self):
        central = QWidget(); self.setCentralWidget(central)
        root = QHBoxLayout(central); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        sidebar = QFrame(); sidebar.setObjectName("sidebar"); sidebar.setFixedWidth(230)
        side = QVBoxLayout(sidebar); side.setContentsMargins(12,18,12,16)
        brand = QLabel("ASART"); brand.setObjectName("brand")
        sub = QLabel(tr("app_title", self.language).upper()); sub.setObjectName("brandSub")
        self.nav = QListWidget(); self.nav.setObjectName("nav")
        for key in ["dashboard", "inbox", "transactions", "documents", "reports", "audit_trail"]:
            self.nav.addItem(QListWidgetItem(tr(key, self.language)))
        self.nav.setCurrentRow(0); self.nav.currentRowChanged.connect(self._navigate)
        side.addWidget(brand); side.addWidget(sub); side.addWidget(self.nav,1)
        self.sidebar_status = QLabel(tr("local_database", self.language)); self.sidebar_status.setStyleSheet("color:#8f9bb3;padding:8px;")
        side.addWidget(self.sidebar_status)

        content_wrap = QWidget(); content_layout = QVBoxLayout(content_wrap); content_layout.setContentsMargins(26,22,26,22)
        self.stack = QStackedWidget(); content_layout.addWidget(self.stack)
        self.pages = []
        self._build_dashboard(); self._build_inbox(); self._build_transactions(); self._build_documents(); self._build_reports(); self._build_audit()
        root.addWidget(sidebar); root.addWidget(content_wrap,1)

    def _navigate(self, row: int):
        if row >= 0:
            self.stack.setCurrentIndex(row)
            if row == 1: self.refresh_inbox()
            elif row == 2: self.refresh_transactions()
            elif row == 3: self.refresh_documents()
            elif row == 4: self.refresh_report()
            elif row == 5: self.refresh_audit()

    def _build_menu(self):
        filem = self.menuBar().addMenu(tr("file", self.language))
        a = QAction(tr("settings", self.language), self); a.triggered.connect(self.open_settings); filem.addAction(a)
        b = QAction(tr("backup_now", self.language), self); b.triggered.connect(self.backup_now); filem.addAction(b)
        o = QAction(tr("open_data_folder", self.language), self); o.triggered.connect(lambda: open_path(self.paths.root)); filem.addAction(o)
        filem.addSeparator(); q = QAction(tr("exit", self.language),self); q.triggered.connect(self.close); filem.addAction(q)

    def _add_page(self, page: QWidget):
        self.pages.append(page); self.stack.addWidget(page)

    def _build_dashboard(self):
        page = QWidget(); lay = QVBoxLayout(page); lay.setContentsMargins(0,0,0,0); lay.setSpacing(16)
        header, hr = make_page_header(tr("dashboard",self.language), tr("dashboard_sub",self.language))
        self.period = QComboBox();
        for key in ["this_month", "this_quarter", "this_year"]: self.period.addItem(tr(key,self.language), key)
        self.period.currentIndexChanged.connect(self.refresh_dashboard)
        new_exp = QPushButton("+ " + tr("expense",self.language)); new_exp.setObjectName("primary"); new_exp.clicked.connect(lambda:self.new_tx("expense"))
        new_inc = QPushButton("+ " + tr("income",self.language)); new_inc.clicked.connect(lambda:self.new_tx("income"))
        hr.addWidget(self.period); hr.addWidget(new_inc); hr.addWidget(new_exp)
        lay.addWidget(header)

        self.cards = {k:KpiCard(tr(key,self.language)) for k,key in [("income","revenue"),("expense","expenses"),("profit","profit_net"),("vat","vat_balance")]}
        cards = QGridLayout(); cards.setSpacing(12)
        for i,k in enumerate(["income","expense","profit","vat"]): cards.addWidget(self.cards[k],0,i)
        lay.addLayout(cards)

        mid = QHBoxLayout(); mid.setSpacing(12)
        task = QFrame(); task.setObjectName("taskBox"); tl = QVBoxLayout(task); tl.setContentsMargins(18,16,18,16)
        QLabel_title = QLabel(tr("documents_review",self.language)); QLabel_title.setStyleSheet("font-weight:600;")
        self.task_count = QLabel("0"); self.task_count.setObjectName("taskCount")
        task_text = QLabel(tr("documents_review_text",self.language)); task_text.setWordWrap(True); task_text.setObjectName("muted")
        inbox_btn = QPushButton(tr("open_inbox",self.language)); inbox_btn.clicked.connect(lambda:self.nav.setCurrentRow(1))
        tl.addWidget(QLabel_title); tl.addWidget(self.task_count); tl.addWidget(task_text); tl.addWidget(inbox_btn); tl.addStretch()
        mid.addWidget(task,1)

        recent_card = QFrame(); recent_card.setProperty("class","card"); rl = QVBoxLayout(recent_card); rl.setContentsMargins(16,14,16,16)
        rtitle = QLabel(tr("recent_transactions",self.language)); rtitle.setStyleSheet("font-weight:600;font-size:12pt;")
        self.recent = QTableWidget(0,6); self.recent.setHorizontalHeaderLabels([tr("date",self.language),tr("type",self.language),tr("counterparty",self.language),tr("description",self.language),tr("gross",self.language),tr("docs",self.language)])
        self._configure_table(self.recent); self.recent.setMaximumHeight(300)
        rl.addWidget(rtitle); rl.addWidget(self.recent)
        mid.addWidget(recent_card,3)
        lay.addLayout(mid,1)
        self._add_page(page)

    def _build_inbox(self):
        page = QWidget(); lay = QVBoxLayout(page); lay.setContentsMargins(0,0,0,0); lay.setSpacing(14)
        header, hr = make_page_header(tr("inbox",self.language), tr("inbox_sub",self.language))
        upload = QPushButton(tr("upload_documents",self.language)); upload.clicked.connect(self.import_document_only)
        camera = QPushButton(tr("capture_photo",self.language)); camera.setObjectName("primary"); camera.clicked.connect(self.photo_document_only)
        hr.addWidget(upload); hr.addWidget(camera); lay.addWidget(header)

        info = QFrame(); info.setProperty("class","card"); il=QHBoxLayout(info); il.setContentsMargins(16,12,16,12)
        self.inbox_status = QLabel(); self.inbox_status.setWordWrap(True)
        il.addWidget(self.inbox_status,1); lay.addWidget(info)

        self.inbox_table = QTableWidget(0,5); self.inbox_table.setHorizontalHeaderLabels(["ID",tr("captured",self.language),tr("file_name",self.language),tr("type",self.language),tr("size",self.language)]); self._configure_table(self.inbox_table)
        self.inbox_table.doubleClicked.connect(self.open_selected_inbox_document)
        lay.addWidget(self.inbox_table,1)
        actions = QHBoxLayout();
        open_btn=QPushButton(tr("open_document",self.language)); open_btn.clicked.connect(self.open_selected_inbox_document)
        exp=QPushButton(tr("book_expense",self.language)); exp.setObjectName("primary"); exp.clicked.connect(lambda:self.book_inbox("expense"))
        inc=QPushButton(tr("book_income",self.language)); inc.clicked.connect(lambda:self.book_inbox("income"))
        actions.addWidget(open_btn); actions.addStretch(); actions.addWidget(inc); actions.addWidget(exp)
        lay.addLayout(actions)
        self._add_page(page)

    def _build_transactions(self):
        page = QWidget(); lay = QVBoxLayout(page); lay.setContentsMargins(0,0,0,0); lay.setSpacing(14)
        header, hr = make_page_header(tr("transactions",self.language), tr("transactions_sub",self.language))
        ex=QPushButton("+ " + tr("expense",self.language)); ex.setObjectName("primary"); ex.clicked.connect(lambda:self.new_tx("expense"))
        inc=QPushButton("+ " + tr("income",self.language)); inc.clicked.connect(lambda:self.new_tx("income"))
        hr.addWidget(inc); hr.addWidget(ex); lay.addWidget(header)

        filters = QHBoxLayout()
        self.tx_search = QLineEdit(); self.tx_search.setPlaceholderText(tr("search_transactions",self.language))
        self.tx_kind = QComboBox();
        for key in ["all","expense","income"]: self.tx_kind.addItem(tr(key,self.language), key)
        self.tx_search.textChanged.connect(self.refresh_transactions); self.tx_kind.currentIndexChanged.connect(self.refresh_transactions)
        filters.addWidget(self.tx_search,1); filters.addWidget(self.tx_kind); lay.addLayout(filters)

        self.tx_table=QTableWidget(0,10); self.tx_table.setHorizontalHeaderLabels(["ID",tr("date",self.language),tr("type",self.language),tr("counterparty",self.language),tr("category",self.language),tr("description",self.language),tr("net",self.language),tr("vat",self.language),tr("gross",self.language),tr("docs",self.language)])
        self._configure_table(self.tx_table); self.tx_table.doubleClicked.connect(self.edit_selected)
        lay.addWidget(self.tx_table,1)
        row=QHBoxLayout(); edit=QPushButton(tr("edit_selected",self.language)); edit.clicked.connect(self.edit_selected); delete=QPushButton(tr("delete",self.language)); delete.setObjectName("danger"); delete.clicked.connect(self.delete_selected)
        row.addWidget(edit); row.addWidget(delete); row.addStretch(); lay.addLayout(row)
        self._add_page(page)

    def _build_documents(self):
        page = QWidget(); lay = QVBoxLayout(page); lay.setContentsMargins(0,0,0,0); lay.setSpacing(14)
        header, hr = make_page_header(tr("document_archive",self.language), tr("document_archive_sub",self.language))
        b=QPushButton(tr("upload",self.language)); b.clicked.connect(self.import_document_only); c=QPushButton(tr("capture_photo",self.language)); c.setObjectName("primary"); c.clicked.connect(self.photo_document_only)
        hr.addWidget(b); hr.addWidget(c); lay.addWidget(header)
        self.doc_table=QTableWidget(0,6); self.doc_table.setHorizontalHeaderLabels(["ID",tr("captured",self.language),tr("original_file",self.language),tr("type",self.language),"SHA-256",tr("linked",self.language)]); self._configure_table(self.doc_table)
        self.doc_table.doubleClicked.connect(self.open_selected_document); lay.addWidget(self.doc_table,1)
        row=QHBoxLayout(); o=QPushButton(tr("open_selected_document",self.language)); o.clicked.connect(self.open_selected_document); row.addWidget(o); row.addStretch(); lay.addLayout(row)
        self._add_page(page)

    def _build_reports(self):
        page=QWidget(); lay=QVBoxLayout(page); lay.setContentsMargins(0,0,0,0); lay.setSpacing(14)
        header, _ = make_page_header(tr("reports",self.language), tr("reports_sub",self.language)); lay.addWidget(header)
        controls=QFrame(); controls.setProperty("class","card"); top=QHBoxLayout(controls); top.setContentsMargins(16,14,16,14)
        self.rep_preset=QComboBox();
        for key in ["custom","this_week","this_month","this_quarter","this_year"]: self.rep_preset.addItem(tr(key,self.language), key)
        self.rep_preset.currentIndexChanged.connect(self.apply_report_preset)
        self.rep_start=QDateEdit(QDate(QDate.currentDate().year(),1,1)); self.rep_start.setCalendarPopup(True); self.rep_start.setDisplayFormat("dd.MM.yyyy")
        self.rep_end=QDateEdit(QDate.currentDate()); self.rep_end.setCalendarPopup(True); self.rep_end.setDisplayFormat("dd.MM.yyyy")
        calc=QPushButton(tr("calculate",self.language)); calc.clicked.connect(self.refresh_report)
        for key,w in [("preset",self.rep_preset),("from",self.rep_start),("to",self.rep_end)]: top.addWidget(QLabel(tr(key,self.language))); top.addWidget(w)
        top.addWidget(calc); top.addStretch(); lay.addWidget(controls)
        summary=QFrame(); summary.setProperty("class","card"); sl=QVBoxLayout(summary); sl.setContentsMargins(18,16,18,16)
        self.rep_summary=QLabel(); self.rep_summary.setWordWrap(True); self.rep_summary.setStyleSheet("font-size:13pt;line-height:1.4;")
        sl.addWidget(self.rep_summary); lay.addWidget(summary)
        btns=QHBoxLayout()
        for text,fn in [(tr("export_pdf",self.language),self.report_pdf),(tr("export_excel",self.language),self.report_excel),(tr("export_csv",self.language),self.report_csv)]:
            b=QPushButton(text); b.clicked.connect(fn); btns.addWidget(b)
        btns.addStretch(); lay.addLayout(btns)
        note=QLabel(tr("reports_note",self.language)); note.setWordWrap(True); note.setObjectName("muted")
        lay.addWidget(note); lay.addStretch(); self._add_page(page)

    def _build_audit(self):
        page=QWidget(); lay=QVBoxLayout(page); lay.setContentsMargins(0,0,0,0); lay.setSpacing(14)
        header,_=make_page_header(tr("audit_trail",self.language), tr("audit_sub",self.language)); lay.addWidget(header)
        self.audit_table=QTableWidget(0,5); self.audit_table.setHorizontalHeaderLabels([tr("time",self.language),tr("action",self.language),tr("entity",self.language),"ID",tr("summary",self.language)]); self._configure_table(self.audit_table); lay.addWidget(self.audit_table,1)
        self._add_page(page)

    def _configure_table(self, table: QTableWidget):
        table.setSelectionBehavior(QAbstractItemView.SelectRows); table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers); table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); table.verticalHeader().setVisible(False)

    def current_period(self):
        today=date.today(); p=self.period.currentData()
        if p=="this_month": start=today.replace(day=1)
        elif p=="this_quarter": start=today.replace(month=((today.month-1)//3)*3+1,day=1)
        else: start=today.replace(month=1,day=1)
        return start.isoformat(), today.isoformat()

    def refresh_all(self):
        self.refresh_dashboard(); self.refresh_inbox(); self.refresh_transactions(); self.refresh_documents(); self.refresh_report(); self.refresh_audit()
        self.sidebar_status.setText(f"{tr('local_database',self.language)}\n{self.paths.database.name}")

    def refresh_dashboard(self):
        s,e=self.current_period(); t=self.db.dashboard_totals(s,e)
        values={"income":t["income_gross"],"expense":t["expense_gross"],"profit":t["income_net"]-t["expense_net"],"vat":t["output_vat"]-t["input_vat"]}
        for k,v in values.items(): self.cards[k].value.setText(euro(v))
        self.cards["income"].detail.setText(tr("transactions_in_period",self.language,count=t["count"]))
        self.cards["expense"].detail.setText(tr("gross_outflow",self.language))
        self.cards["profit"].detail.setText(tr("profit_detail",self.language))
        self.cards["vat"].detail.setText(tr("vat_detail",self.language))
        self.task_count.setText(str(self.db.unfiled_document_count()))
        rows=self.db.list_transactions(s,e)[:10]; self.recent.setRowCount(len(rows))
        for i,r in enumerate(rows):
            vals=[r["booking_date"],kind_label(r["kind"],self.language),r.get("counterparty_name") or "",r["description"],euro(r["gross_amount_cents"]),str(r["document_count"])]
            for j,v in enumerate(vals): self.recent.setItem(i,j,QTableWidgetItem(str(v)))

    def refresh_inbox(self):
        rows=self.db.list_unfiled_documents(); self.inbox_table.setRowCount(len(rows))
        self.inbox_status.setText(tr("inbox_waiting",self.language,count=len(rows)) if rows else tr("inbox_clear",self.language))
        for i,r in enumerate(rows):
            vals=[r["id"],r["captured_at"],r["original_name"],document_type_label(r["document_type"],self.language),f"{r['file_size']/1024:.0f} KB"]
            for j,v in enumerate(vals): self.inbox_table.setItem(i,j,QTableWidgetItem(str(v)))
        self.task_count.setText(str(len(rows)))

    def refresh_transactions(self):
        rows=self.db.search_transactions(self.tx_search.text(), self.tx_kind.currentData()); self.tx_table.setRowCount(len(rows))
        for i,r in enumerate(rows):
            vals=[r["id"],r["booking_date"],kind_label(r["kind"],self.language),r.get("counterparty_name") or "",category_label(r.get("category_name") or "",self.language),r["description"],euro(r["net_amount_cents"]),euro(r["vat_amount_cents"]),euro(r["gross_amount_cents"]),r["document_count"]]
            for j,v in enumerate(vals): self.tx_table.setItem(i,j,QTableWidgetItem(str(v)))

    def refresh_documents(self):
        rows=self.db.list_documents(); self.doc_table.setRowCount(len(rows))
        for i,r in enumerate(rows):
            vals=[r["id"],r["captured_at"],r["original_name"],document_type_label(r["document_type"],self.language),r["sha256"][:20]+"…",r["linked_transactions"]]
            for j,v in enumerate(vals): self.doc_table.setItem(i,j,QTableWidgetItem(str(v)))

    def refresh_report(self):
        s,e=qdate_to_iso(self.rep_start.date()),qdate_to_iso(self.rep_end.date()); t=self.db.dashboard_totals(s,e); profit=t["income_net"]-t["expense_net"]; vat=t["output_vat"]-t["input_vat"]
        self.rep_summary.setText(f"<b>{tr('income_net',self.language)}:</b> {euro(t['income_net'])} &nbsp;&nbsp;&nbsp; <b>{tr('expenses_net',self.language)}:</b> {euro(t['expense_net'])}<br><br><b>{tr('profit_net',self.language)}:</b> {euro(profit)} &nbsp;&nbsp;&nbsp; {tr('output_vat',self.language)}: {euro(t['output_vat'])} &nbsp;&nbsp;&nbsp; {tr('input_vat',self.language)}: {euro(t['input_vat'])} &nbsp;&nbsp;&nbsp; <b>{tr('vat_balance',self.language)}:</b> {euro(vat)}<br><br>{tr('transactions_period',self.language)}: {t['count']}")

    def refresh_audit(self):
        rows=self.db.audit_entries(); self.audit_table.setRowCount(len(rows))
        for i,r in enumerate(rows):
            for j,v in enumerate([r["created_at"],r["action"],r["entity_type"],r["entity_id"] or "",r["summary"]]): self.audit_table.setItem(i,j,QTableWidgetItem(str(v)))

    def apply_report_preset(self):
        preset=self.rep_preset.currentData()
        if preset=="custom": return
        today=date.today()
        if preset=="this_week": start=today.fromordinal(today.toordinal()-today.weekday())
        elif preset=="this_month": start=today.replace(day=1)
        elif preset=="this_quarter": start=today.replace(month=((today.month-1)//3)*3+1,day=1)
        else: start=today.replace(month=1,day=1)
        self.rep_start.setDate(QDate(start.year,start.month,start.day)); self.rep_end.setDate(QDate(today.year,today.month,today.day)); self.refresh_report()

    def new_tx(self,kind):
        if TransactionDialog(self.db,self.paths,kind,parent=self).exec()==QDialog.Accepted: self.refresh_all()

    def selected_tx_id(self):
        row=self.tx_table.currentRow(); return int(self.tx_table.item(row,0).text()) if row>=0 else None

    def edit_selected(self,*_):
        tid=self.selected_tx_id()
        if tid is None: return
        tx=self.db.get_transaction(tid)
        if tx and TransactionDialog(self.db,self.paths,tx["kind"],tid,parent=self).exec()==QDialog.Accepted: self.refresh_all()

    def delete_selected(self):
        tid=self.selected_tx_id()
        if tid is None:return
        if ask_yes_no(self,tr("delete_transaction",self.language),tr("delete_transaction_msg",self.language),self.language):
            self.db.delete_transaction(tid); self.refresh_all()

    def _selected_inbox_document_id(self):
        row=self.inbox_table.currentRow(); return int(self.inbox_table.item(row,0).text()) if row>=0 else None

    def book_inbox(self, kind: str):
        did=self._selected_inbox_document_id()
        if did is None:
            QMessageBox.information(self,tr("select_document",self.language),tr("select_document_msg",self.language)); return
        if TransactionDialog(self.db,self.paths,kind,preset_document_ids=[did],parent=self).exec()==QDialog.Accepted:
            self.refresh_all()

    def open_selected_inbox_document(self,*_):
        did=self._selected_inbox_document_id()
        if did is None:return
        doc=self.db.get_document(did)
        if doc and Path(doc["stored_path"]).exists(): open_path(doc["stored_path"])

    def import_document_only(self):
        files,_=QFileDialog.getOpenFileNames(self,tr("import_documents",self.language),"",tr("documents_filter",self.language))
        for f in files:
            try: archive_document(self.db,self.paths,Path(f),"unfiled")
            except Exception as exc: QMessageBox.critical(self,tr("import_failed",self.language),str(exc))
        self.refresh_all(); self.nav.setCurrentRow(1)

    def photo_document_only(self):
        dlg=CameraDialog(self, self.language)
        if dlg.exec()==QDialog.Accepted and dlg.saved_path:
            try: archive_document(self.db,self.paths,dlg.saved_path,"unfiled_photo")
            except Exception as exc: QMessageBox.critical(self,tr("capture_failed",self.language),str(exc))
            finally:
                try: dlg.saved_path.unlink(missing_ok=True)
                except Exception: pass
            self.refresh_all(); self.nav.setCurrentRow(1)

    def open_selected_document(self,*_):
        row=self.doc_table.currentRow()
        if row<0:return
        did=int(self.doc_table.item(row,0).text()); doc=self.db.get_document(did)
        if doc and Path(doc["stored_path"]).exists(): open_path(doc["stored_path"])

    def open_settings(self):
        old_language = self.language
        if SettingsDialog(self.db,self).exec()==QDialog.Accepted:
            self.language = self.db.get_language()
            company = self.db.get_company()
            self.setWindowTitle(f"{company['company_name']} – {tr('app_title', self.language)}")
            if self.language != old_language:
                self.menuBar().clear()
                old_central = self.takeCentralWidget()
                if old_central is not None:
                    old_central.deleteLater()
                self._build_shell()
                self._build_menu()
            self.refresh_all()

    def backup_now(self):
        try: p=create_backup(self.paths); QMessageBox.information(self,tr("backup_created",self.language),tr("backup_saved_to",self.language,path=p))
        except Exception as exc: QMessageBox.critical(self,tr("backup_failed",self.language),str(exc))

    def _report_range(self): return qdate_to_iso(self.rep_start.date()),qdate_to_iso(self.rep_end.date())
    def _show_export(self,p): QMessageBox.information(self,tr("export_created",self.language),tr("saved_to",self.language,path=p))
    def report_pdf(self):
        try: self._show_export(export_pdf(self.db,self.paths,*self._report_range()))
        except Exception as exc: QMessageBox.critical(self,tr("export_failed",self.language),str(exc))
    def report_excel(self):
        try: self._show_export(export_excel(self.db,self.paths,*self._report_range()))
        except Exception as exc: QMessageBox.critical(self,tr("export_failed",self.language),str(exc))
    def report_csv(self):
        try: self._show_export(export_csv(self.db,self.paths,*self._report_range()))
        except Exception as exc: QMessageBox.critical(self,tr("export_failed",self.language),str(exc))

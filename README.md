# Asart Bookkeeping

A local-first Windows bookkeeping and document-archive application for a German small business.

## What works now

- Income and expense entry with booking date and document date
- Net / VAT / gross calculation for 0%, 7% and 19% VAT
- Supplier/customer tracking
- Editable bookkeeping categories
- Payment method, paid status and deductible percentage
- Receipt/PDF/image attachment to transactions
- Standalone document inbox/archive
- Webcam receipt photo capture when a camera is available
- Archived originals are copied into year/month folders and SHA-256 fingerprinted
- Dashboard for current month, quarter and year
- Report presets for week, month, quarter and year, plus custom dates
- PDF, Excel and semicolon-delimited CSV exports
- VAT output/input/balance summary
- Net profit summary suitable as a bookkeeping preparation view
- Append-only application audit log for create/edit/delete actions
- Consistent database + document ZIP backups
- Local SQLite storage
- Windows desktop shortcut installer
- PyInstaller build script for a normal Windows executable

## Data location

By default the app stores its persistent data under:

`%USERPROFILE%\\Documents\\Asart Bookkeeping\\`

with:

- `bookkeeping.db` — SQLite accounting database
- `documents\\` — archived source documents
- `exports\\` — generated reports
- `backups\\` — ZIP backups

The source program folder can therefore be replaced or upgraded without deleting the bookkeeping data.

## Install on Windows (recommended for first use)

1. Install Python 3.11 or 3.12 from python.org. During setup enable **Add Python to PATH**.
2. Extract this project to a permanent folder, for example `C:\\AsartBookkeeping`.
3. Double-click `install_dev_windows.bat`.
4. The script creates a private virtual environment, installs the required packages and creates an **Asart Bookkeeping** desktop shortcut.
5. Start it from the desktop shortcut.
6. Open **File → Company & tax settings** before entering real transactions.

The first installation requires Internet access for the Python packages. Once installed, normal operation is local and does not need Internet access.

## Build a standalone EXE

Double-click `build_windows.bat`.

The resulting program is placed under:

`dist\\Asart Bookkeeping\\Asart Bookkeeping.exe`

PyInstaller's folder build is intentionally used rather than a single-file executable because startup is faster and Qt/OpenCV packaging is more reliable.

## Backups

Use **File → Create backup now**. The backup uses SQLite's live backup mechanism and copies the archived documents into a timestamped ZIP under the `backups` folder.

Keep at least one additional copy on a physically separate drive or another protected storage location.

## Documents and immutability

When a document is attached or imported, the application copies the original into its archive and stores a SHA-256 fingerprint. Editing a transaction does not overwrite the archived source file. Deleting a transaction does not delete the archived source document.

The application audit trail records creation, edits and deletions performed through the application.

## Tax / Finanzamt scope

This version is intended to maintain bookkeeping records and prepare/export figures. It does **not** transmit tax returns to ELSTER yet. VAT and profit summaries should be reviewed before they are used for a tax filing. ERiC/ELSTER, DATEV export, structured E-Rechnung processing and automated bank reconciliation are natural later modules.

The application is designed with traceability and source-document retention in mind, but no custom program should be described as legally certified merely because it has those controls. Your actual retention, procedural documentation, tax configuration and use of the system remain part of compliance.

## Run from a terminal

```powershell
.venv\\Scripts\\activate
python run.py
```

## Developer tests

```powershell
python -m pytest -q
```

## Project layout

- `app/db.py` — SQLite schema and accounting persistence
- `app/documents.py` — archive and SHA-256 fingerprinting
- `app/reports.py` — PDF/Excel/CSV exports
- `app/backup.py` — consistent local backups
- `app/ui.py` — Windows Qt user interface
- `app/main.py` — application startup
- `tests/` — accounting-core tests

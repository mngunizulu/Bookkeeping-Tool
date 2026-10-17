from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import Any, Iterable

DB_SCHEMA_VERSION = 3


@dataclass(slots=True)
class AppPaths:
    root: Path
    database: Path
    documents: Path
    exports: Path
    backups: Path


def default_paths(company_slug: str = "Asart Bookkeeping") -> AppPaths:
    root = Path.home() / "Documents" / company_slug
    paths = AppPaths(
        root=root,
        database=root / "bookkeeping.db",
        documents=root / "documents",
        exports=root / "exports",
        backups=root / "backups",
    )
    for p in (paths.root, paths.documents, paths.exports, paths.backups):
        p.mkdir(parents=True, exist_ok=True)
    return paths


class Database:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def connect(self):
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA journal_mode=WAL")
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def _init_schema(self):
        with self.connect() as con:
            con.executescript(
                """
                CREATE TABLE IF NOT EXISTS meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS company_settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    company_name TEXT NOT NULL DEFAULT 'My Business',
                    owner_name TEXT DEFAULT '',
                    street TEXT DEFAULT '',
                    postal_code TEXT DEFAULT '',
                    city TEXT DEFAULT '',
                    tax_number TEXT DEFAULT '',
                    vat_id TEXT DEFAULT '',
                    iban TEXT DEFAULT '',
                    kleinunternehmer INTEGER NOT NULL DEFAULT 0,
                    fiscal_year_start_month INTEGER NOT NULL DEFAULT 1,
                    language TEXT NOT NULL DEFAULT 'en',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    kind TEXT NOT NULL CHECK(kind IN ('income','expense','both')),
                    tax_code TEXT DEFAULT '',
                    active INTEGER NOT NULL DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS counterparties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    kind TEXT NOT NULL DEFAULT 'supplier' CHECK(kind IN ('supplier','customer','both')),
                    vat_id TEXT DEFAULT '',
                    email TEXT DEFAULT '',
                    notes TEXT DEFAULT '',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_name TEXT NOT NULL,
                    stored_path TEXT NOT NULL,
                    sha256 TEXT NOT NULL,
                    mime_type TEXT DEFAULT '',
                    file_size INTEGER NOT NULL,
                    document_type TEXT NOT NULL DEFAULT 'receipt',
                    captured_at TEXT NOT NULL,
                    notes TEXT DEFAULT '',
                    UNIQUE(sha256, stored_path)
                );

                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    booking_date TEXT NOT NULL,
                    document_date TEXT,
                    kind TEXT NOT NULL CHECK(kind IN ('income','expense')),
                    counterparty_id INTEGER,
                    category_id INTEGER,
                    description TEXT NOT NULL,
                    document_number TEXT DEFAULT '',
                    net_amount_cents INTEGER NOT NULL,
                    vat_rate REAL NOT NULL DEFAULT 0,
                    vat_amount_cents INTEGER NOT NULL DEFAULT 0,
                    gross_amount_cents INTEGER NOT NULL,
                    payment_method TEXT DEFAULT 'Bank',
                    paid INTEGER NOT NULL DEFAULT 1,
                    tax_deductible_percent REAL NOT NULL DEFAULT 100,
                    notes TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(counterparty_id) REFERENCES counterparties(id),
                    FOREIGN KEY(category_id) REFERENCES categories(id)
                );

                CREATE TABLE IF NOT EXISTS transaction_documents (
                    transaction_id INTEGER NOT NULL,
                    document_id INTEGER NOT NULL,
                    PRIMARY KEY(transaction_id, document_id),
                    FOREIGN KEY(transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
                    FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE RESTRICT
                );

                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    action TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id INTEGER,
                    summary TEXT NOT NULL
                );
                """
            )
            # Backward-compatible schema migration for databases created by v0.2.0 and earlier.
            company_columns = {row[1] for row in con.execute("PRAGMA table_info(company_settings)").fetchall()}
            if "language" not in company_columns:
                con.execute("ALTER TABLE company_settings ADD COLUMN language TEXT NOT NULL DEFAULT 'en'")

            now = datetime.now().isoformat(timespec="seconds")
            con.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('schema_version', ?)", (str(DB_SCHEMA_VERSION),))
            con.execute("UPDATE meta SET value=? WHERE key='schema_version'", (str(DB_SCHEMA_VERSION),))
            con.execute(
                "INSERT OR IGNORE INTO company_settings(id, created_at, updated_at) VALUES(1, ?, ?)",
                (now, now),
            )
            defaults = [
                ("Sales / Revenue", "income", ""),
                ("Other Income", "income", ""),
                ("Goods / Raw materials", "expense", ""),
                ("Packaging", "expense", ""),
                ("Shipping / Postage", "expense", ""),
                ("Advertising / Marketing", "expense", ""),
                ("Website / Software", "expense", ""),
                ("Office Supplies", "expense", ""),
                ("Telephone / Internet", "expense", ""),
                ("Professional Fees", "expense", ""),
                ("Insurance", "expense", ""),
                ("Bank Fees", "expense", ""),
                ("Travel", "expense", ""),
                ("Vehicle", "expense", ""),
                ("Equipment", "expense", ""),
                ("Other Operating Expenses", "expense", ""),
            ]
            con.executemany("INSERT OR IGNORE INTO categories(name,kind,tax_code) VALUES(?,?,?)", defaults)

    def audit(self, action: str, entity_type: str, entity_id: int | None, summary: str):
        with self.connect() as con:
            con.execute(
                "INSERT INTO audit_log(created_at, action, entity_type, entity_id, summary) VALUES(?,?,?,?,?)",
                (datetime.now().isoformat(timespec="seconds"), action, entity_type, entity_id, summary),
            )

    def get_company(self) -> dict[str, Any]:
        with self.connect() as con:
            row = con.execute("SELECT * FROM company_settings WHERE id=1").fetchone()
            return dict(row)

    def get_language(self) -> str:
        company = self.get_company()
        language = company.get("language") or "en"
        return language if language in {"en", "de"} else "en"

    def save_company(self, values: dict[str, Any]):
        allowed = {
            "company_name", "owner_name", "street", "postal_code", "city", "tax_number",
            "vat_id", "iban", "kleinunternehmer", "fiscal_year_start_month", "language"
        }
        payload = {k: v for k, v in values.items() if k in allowed}
        if not payload:
            return
        payload["updated_at"] = datetime.now().isoformat(timespec="seconds")
        set_sql = ", ".join(f"{k}=?" for k in payload)
        with self.connect() as con:
            con.execute(f"UPDATE company_settings SET {set_sql} WHERE id=1", tuple(payload.values()))
        self.audit("UPDATE", "company_settings", 1, "Company settings updated")

    def list_categories(self, kind: str | None = None) -> list[dict[str, Any]]:
        sql = "SELECT * FROM categories WHERE active=1"
        params: list[Any] = []
        if kind:
            sql += " AND kind IN (?, 'both')"
            params.append(kind)
        sql += " ORDER BY name"
        with self.connect() as con:
            return [dict(r) for r in con.execute(sql, params).fetchall()]

    def add_category(self, name: str, kind: str):
        with self.connect() as con:
            cur = con.execute("INSERT INTO categories(name,kind) VALUES(?,?)", (name.strip(), kind))
            cid = cur.lastrowid
        self.audit("CREATE", "category", cid, f"Category created: {name}")
        return cid

    def list_counterparties(self, kind: str | None = None) -> list[dict[str, Any]]:
        sql = "SELECT * FROM counterparties"
        params: list[Any] = []
        if kind:
            sql += " WHERE kind IN (?, 'both')"
            params.append(kind)
        sql += " ORDER BY name"
        with self.connect() as con:
            return [dict(r) for r in con.execute(sql, params).fetchall()]

    def get_or_create_counterparty(self, name: str, kind: str) -> int | None:
        name = name.strip()
        if not name:
            return None
        with self.connect() as con:
            row = con.execute("SELECT id FROM counterparties WHERE lower(name)=lower(?) LIMIT 1", (name,)).fetchone()
            if row:
                return int(row["id"])
            cur = con.execute(
                "INSERT INTO counterparties(name,kind,created_at) VALUES(?,?,?)",
                (name, kind, datetime.now().isoformat(timespec="seconds")),
            )
            cid = int(cur.lastrowid)
        self.audit("CREATE", "counterparty", cid, f"Counterparty created: {name}")
        return cid

    def add_document(self, *, original_name: str, stored_path: str, sha256: str, mime_type: str,
                     file_size: int, document_type: str = "receipt", notes: str = "") -> int:
        with self.connect() as con:
            cur = con.execute(
                """INSERT INTO documents(original_name,stored_path,sha256,mime_type,file_size,document_type,captured_at,notes)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (original_name, stored_path, sha256, mime_type, file_size, document_type,
                 datetime.now().isoformat(timespec="seconds"), notes),
            )
            did = int(cur.lastrowid)
        self.audit("CREATE", "document", did, f"Document archived: {original_name} [{sha256[:12]}]")
        return did

    def add_transaction(self, tx: dict[str, Any], document_ids: Iterable[int] = ()) -> int:
        now = datetime.now().isoformat(timespec="seconds")
        fields = [
            "booking_date", "document_date", "kind", "counterparty_id", "category_id", "description",
            "document_number", "net_amount_cents", "vat_rate", "vat_amount_cents", "gross_amount_cents",
            "payment_method", "paid", "tax_deductible_percent", "notes"
        ]
        values = [tx.get(f) for f in fields]
        with self.connect() as con:
            cur = con.execute(
                f"INSERT INTO transactions({','.join(fields)},created_at,updated_at) VALUES({','.join('?' for _ in fields)},?,?)",
                (*values, now, now),
            )
            tid = int(cur.lastrowid)
            con.executemany(
                "INSERT OR IGNORE INTO transaction_documents(transaction_id,document_id) VALUES(?,?)",
                [(tid, int(d)) for d in document_ids],
            )
        self.audit("CREATE", "transaction", tid, f"{tx['kind']} {tx['gross_amount_cents']/100:.2f} EUR: {tx['description']}")
        return tid

    def update_transaction(self, tid: int, tx: dict[str, Any], document_ids: Iterable[int] | None = None):
        fields = [
            "booking_date", "document_date", "kind", "counterparty_id", "category_id", "description",
            "document_number", "net_amount_cents", "vat_rate", "vat_amount_cents", "gross_amount_cents",
            "payment_method", "paid", "tax_deductible_percent", "notes"
        ]
        values = [tx.get(f) for f in fields]
        with self.connect() as con:
            con.execute(
                f"UPDATE transactions SET {','.join(f'{f}=?' for f in fields)},updated_at=? WHERE id=?",
                (*values, datetime.now().isoformat(timespec="seconds"), tid),
            )
            if document_ids is not None:
                con.execute("DELETE FROM transaction_documents WHERE transaction_id=?", (tid,))
                con.executemany(
                    "INSERT OR IGNORE INTO transaction_documents(transaction_id,document_id) VALUES(?,?)",
                    [(tid, int(d)) for d in document_ids],
                )
        self.audit("UPDATE", "transaction", tid, f"Transaction updated: {tx['description']}")

    def delete_transaction(self, tid: int):
        with self.connect() as con:
            row = con.execute("SELECT description,gross_amount_cents FROM transactions WHERE id=?", (tid,)).fetchone()
            if not row:
                return
            con.execute("DELETE FROM transactions WHERE id=?", (tid,))
        self.audit("DELETE", "transaction", tid, f"Deleted transaction: {row['description']} ({row['gross_amount_cents']/100:.2f} EUR)")

    def list_transactions(self, start: str | None = None, end: str | None = None, kind: str | None = None) -> list[dict[str, Any]]:
        sql = """
            SELECT t.*, c.name AS category_name, cp.name AS counterparty_name,
                   (SELECT COUNT(*) FROM transaction_documents td WHERE td.transaction_id=t.id) AS document_count
            FROM transactions t
            LEFT JOIN categories c ON c.id=t.category_id
            LEFT JOIN counterparties cp ON cp.id=t.counterparty_id
            WHERE 1=1
        """
        params: list[Any] = []
        if start:
            sql += " AND t.booking_date>=?"; params.append(start)
        if end:
            sql += " AND t.booking_date<=?"; params.append(end)
        if kind:
            sql += " AND t.kind=?"; params.append(kind)
        sql += " ORDER BY t.booking_date DESC, t.id DESC"
        with self.connect() as con:
            return [dict(r) for r in con.execute(sql, params).fetchall()]

    def get_transaction(self, tid: int) -> dict[str, Any] | None:
        with self.connect() as con:
            row = con.execute("SELECT * FROM transactions WHERE id=?", (tid,)).fetchone()
            return dict(row) if row else None

    def documents_for_transaction(self, tid: int) -> list[dict[str, Any]]:
        with self.connect() as con:
            rows = con.execute(
                """SELECT d.* FROM documents d JOIN transaction_documents td ON td.document_id=d.id
                   WHERE td.transaction_id=? ORDER BY d.id""", (tid,)
            ).fetchall()
            return [dict(r) for r in rows]

    def list_documents(self) -> list[dict[str, Any]]:
        with self.connect() as con:
            rows = con.execute(
                """SELECT d.*, COUNT(td.transaction_id) AS linked_transactions
                   FROM documents d LEFT JOIN transaction_documents td ON td.document_id=d.id
                   GROUP BY d.id ORDER BY d.captured_at DESC"""
            ).fetchall()
            return [dict(r) for r in rows]


    def list_unfiled_documents(self) -> list[dict[str, Any]]:
        """Documents that are not yet linked to a bookkeeping transaction."""
        with self.connect() as con:
            rows = con.execute(
                """SELECT d.*
                   FROM documents d
                   LEFT JOIN transaction_documents td ON td.document_id=d.id
                   WHERE td.document_id IS NULL
                   ORDER BY d.captured_at DESC"""
            ).fetchall()
            return [dict(r) for r in rows]

    def unfiled_document_count(self) -> int:
        with self.connect() as con:
            row = con.execute(
                """SELECT COUNT(*) AS n
                   FROM documents d
                   LEFT JOIN transaction_documents td ON td.document_id=d.id
                   WHERE td.document_id IS NULL"""
            ).fetchone()
            return int(row["n"] if row else 0)

    def search_transactions(self, query: str = "", kind: str | None = None) -> list[dict[str, Any]]:
        """Search the ledger without changing the existing list_transactions API."""
        sql = """
            SELECT t.*, c.name AS category_name, cp.name AS counterparty_name,
                   (SELECT COUNT(*) FROM transaction_documents td WHERE td.transaction_id=t.id) AS document_count
            FROM transactions t
            LEFT JOIN categories c ON c.id=t.category_id
            LEFT JOIN counterparties cp ON cp.id=t.counterparty_id
            WHERE 1=1
        """
        params: list[Any] = []
        if kind and kind != "all":
            sql += " AND t.kind=?"
            params.append(kind)
        query = (query or "").strip()
        if query:
            like = f"%{query}%"
            sql += """ AND (t.description LIKE ? OR t.document_number LIKE ?
                            OR COALESCE(cp.name,'') LIKE ? OR COALESCE(c.name,'') LIKE ?
                            OR t.booking_date LIKE ?)"""
            params.extend([like, like, like, like, like])
        sql += " ORDER BY t.booking_date DESC, t.id DESC"
        with self.connect() as con:
            return [dict(r) for r in con.execute(sql, params).fetchall()]

    def get_document(self, document_id: int) -> dict[str, Any] | None:
        with self.connect() as con:
            row = con.execute("SELECT * FROM documents WHERE id=?", (document_id,)).fetchone()
            return dict(row) if row else None

    def dashboard_totals(self, start: str, end: str) -> dict[str, int]:
        with self.connect() as con:
            row = con.execute(
                """SELECT
                    COALESCE(SUM(CASE WHEN kind='income' THEN gross_amount_cents ELSE 0 END),0) AS income_gross,
                    COALESCE(SUM(CASE WHEN kind='expense' THEN gross_amount_cents ELSE 0 END),0) AS expense_gross,
                    COALESCE(SUM(CASE WHEN kind='income' THEN net_amount_cents ELSE 0 END),0) AS income_net,
                    COALESCE(SUM(CASE WHEN kind='expense' THEN net_amount_cents ELSE 0 END),0) AS expense_net,
                    COALESCE(SUM(CASE WHEN kind='income' THEN vat_amount_cents ELSE 0 END),0) AS output_vat,
                    COALESCE(SUM(CASE WHEN kind='expense' THEN vat_amount_cents ELSE 0 END),0) AS input_vat,
                    COUNT(*) AS count
                    FROM transactions WHERE booking_date BETWEEN ? AND ?""", (start, end)
            ).fetchone()
            return dict(row)

    def audit_entries(self, limit: int = 500) -> list[dict[str, Any]]:
        with self.connect() as con:
            return [dict(r) for r in con.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]

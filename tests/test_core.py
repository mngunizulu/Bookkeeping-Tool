from pathlib import Path
from tempfile import TemporaryDirectory
from app.db import Database


def test_transaction_totals():
    with TemporaryDirectory() as d:
        db = Database(Path(d)/"test.db")
        cat = db.list_categories("expense")[0]["id"]
        tx = dict(booking_date="2026-09-01",document_date="2026-09-01",kind="expense",counterparty_id=None,category_id=cat,
                  description="Test",document_number="",net_amount_cents=10000,vat_rate=19,vat_amount_cents=1900,gross_amount_cents=11900,
                  payment_method="Bank",paid=1,tax_deductible_percent=100,notes="")
        db.add_transaction(tx)
        t=db.dashboard_totals("2026-09-01","2026-09-30")
        assert t["expense_net"]==10000
        assert t["input_vat"]==1900
        assert t["expense_gross"]==11900

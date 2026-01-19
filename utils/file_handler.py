from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

EXPECTED_FIELDS = [
    "TransactionID", "Date", "ProductID", "ProductName",
    "Quantity", "UnitPrice", "CustomerID", "Region"
]

@dataclass(frozen=True)
class SalesRecord:
    transaction_id: str
    date: str
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    customer_id: str
    region: str

    @property
    def revenue(self) -> float:
        return self.quantity * self.unit_price


def _decode_bytes(raw: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="replace")


def _clean_number(s: str) -> str:
    return s.replace(",", "").strip()


def _clean_product_name(s: str) -> str:
    return s.replace(",", "").strip()


def _parse_pipe_row(line: str) -> Optional[Dict[str, str]]:
    line = line.strip()
    if not line:
        return None

    parts = line.split("|")

    # Skip header row if present
    if parts and parts[0].strip() == "TransactionID":
        return None

    # If extra fields exist, assume ProductName may contain pipes.
    # Map: [0]=TID [1]=Date [2]=ProdID [3..-5]=ProductName [-4]=Qty [-3]=UnitPrice [-2]=CustomerID [-1]=Region
    if len(parts) > 8:
        tid = parts[0]
        dt = parts[1]
        pid = parts[2]
        product_name = "|".join(parts[3:-4])
        qty = parts[-4]
        price = parts[-3]
        cid = parts[-2]
        region = parts[-1]
        parts = [tid, dt, pid, product_name, qty, price, cid, region]

    # If fewer than 8 fields, pad (will fail validation later)
    if len(parts) < 8:
        parts = parts + ([""] * (8 - len(parts)))

    row = dict(zip(EXPECTED_FIELDS, parts))
    return {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}


def load_and_clean_sales(path: str | Path) -> Tuple[List[SalesRecord], Dict[str, int]]:
    raw = Path(path).read_bytes()
    text = _decode_bytes(raw)
    lines = text.splitlines()

    parsed_rows: List[Dict[str, str]] = []
    for line in lines:
        row = _parse_pipe_row(line)
        if row is not None:
            parsed_rows.append(row)

    total_parsed = len(parsed_rows)
    valid: List[SalesRecord] = []
    invalid = 0

    for r in parsed_rows:
        try:
            tid = r["TransactionID"].strip()
            if not tid.startswith("T"):
                raise ValueError("TransactionID must start with T")

            customer_id = r["CustomerID"].strip()
            region = r["Region"].strip()
            if not customer_id or not region:
                raise ValueError("Missing CustomerID or Region")

            qty = int(_clean_number(r["Quantity"]))
            price = float(_clean_number(r["UnitPrice"]))

            if qty <= 0:
                raise ValueError("Quantity <= 0")
            if price <= 0:
                raise ValueError("UnitPrice <= 0")

            rec = SalesRecord(
                transaction_id=tid,
                date=r["Date"].strip(),
                product_id=r["ProductID"].strip(),
                product_name=_clean_product_name(r["ProductName"]),
                quantity=qty,
                unit_price=price,
                customer_id=customer_id,
                region=region,
            )
            valid.append(rec)
        except Exception:
            invalid += 1

    # REQUIRED printout
    print(f"Total records parsed: {total_parsed}")
    print(f"Invalid records removed: {invalid}")
    print(f"Valid records after cleaning: {len(valid)}")

    stats = {
        "total_parsed": total_parsed,
        "invalid_removed": invalid,
        "valid_after_cleaning": len(valid),
    }
    return valid, stats


from __future__ import annotations

from typing import Dict, List, Optional, Tuple


def read_sales_data(filename: str) -> List[str]:
    """
    Reads sales data from file handling encoding issues
    Returns: list of raw lines (strings)
    Requirements:
    - Use 'with' statement
    - Handle different encodings (try 'utf-8', 'latin-1', 'cp1252')
    - Handle FileNotFoundError with appropriate error message
    - Skip the header row
    - Remove empty lines
    """
    encodings = ["utf-8", "latin-1", "cp1252"]

    try:
        for enc in encodings:
            try:
                with open(filename, "r", encoding=enc) as f:
                    lines = f.read().splitlines()
                break
            except UnicodeDecodeError:
                lines = None
                continue

        if lines is None:
            # last resort: replace bad chars
            with open(filename, "r", encoding="latin-1", errors="replace") as f:
                lines = f.read().splitlines()

    except FileNotFoundError:
        print(f"Error: File not found -> {filename}")
        return []

    # remove empty lines
    lines = [ln.strip() for ln in lines if ln and ln.strip()]

    # skip header row if present
    if lines and lines[0].startswith("TransactionID"):
        lines = lines[1:]

    return lines


def parse_transactions(raw_lines: List[str]) -> List[Dict]:
    """
    Parses raw lines into clean list of dictionaries
    Returns: list of dictionaries with keys:
    ['TransactionID','Date','ProductID','ProductName','Quantity','UnitPrice','CustomerID','Region']

    Requirements:
    - Split by pipe delimiter '|'
    - Handle commas within ProductName (remove or replace)
    - Remove commas from numeric fields and convert to proper types
    - Convert Quantity to int
    - Convert UnitPrice to float
    - Skip rows with incorrect number of fields
    """
    out: List[Dict] = []
    keys = ["TransactionID", "Date", "ProductID", "ProductName", "Quantity", "UnitPrice", "CustomerID", "Region"]

    for line in raw_lines:
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 8:
            continue

        txid, dt, pid, pname, qty, price, cid, region = parts

        # clean product name commas
        pname = pname.replace(",", "")

        # remove commas from numbers (e.g., 1,500 -> 1500)
        qty_clean = qty.replace(",", "")
        price_clean = price.replace(",", "")

        try:
            qty_int = int(qty_clean)
            price_float = float(price_clean)
        except ValueError:
            continue

        rec = {
            "TransactionID": txid,
            "Date": dt,
            "ProductID": pid,
            "ProductName": pname,
            "Quantity": qty_int,
            "UnitPrice": price_float,
            "CustomerID": cid,
            "Region": region,
        }
        out.append(rec)

    return out


def validate_and_filter(
    transactions: List[Dict],
    region: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
) -> Tuple[List[Dict], int, Dict]:
    """
    Validates transactions and applies optional filters

    Returns: (valid_transactions, invalid_count, filter_summary)

    Validation Rules:
    - Quantity must be > 0
    - UnitPrice must be > 0
    - All required fields must be present
    - TransactionID must start with 'T'
    - ProductID must start with 'P'
    - CustomerID must start with 'C'

    Filter Display:
    - Print available regions to user before filtering
    - Print transaction amount range (min/max) to user
    - Show count of records after each filter applied
    """
    summary = {
        "total_input": len(transactions),
        "invalid": 0,
        "filtered_by_region": 0,
        "filtered_by_amount": 0,
        "final_count": 0,
    }

    required = ["TransactionID", "Date", "ProductID", "ProductName", "Quantity", "UnitPrice", "CustomerID", "Region"]

    valid: List[Dict] = []
    invalid = 0

    for t in transactions:
        try:
            # required fields present and non-empty
            for k in required:
                if k not in t or t[k] in (None, ""):
                    raise ValueError("missing field")

            # type checks (Quantity int, UnitPrice float)
            qty = int(t["Quantity"])
            price = float(t["UnitPrice"])

            if qty <= 0 or price <= 0:
                raise ValueError("qty/price invalid")

            if not str(t["TransactionID"]).startswith("T"):
                raise ValueError("bad transaction id")
            if not str(t["ProductID"]).startswith("P"):
                raise ValueError("bad product id")
            if not str(t["CustomerID"]).startswith("C"):
                raise ValueError("bad customer id")

            # attach computed amount for filtering convenience
            t2 = dict(t)
            t2["_amount"] = qty * price
            valid.append(t2)

        except Exception:
            invalid += 1

    summary["invalid"] = invalid

    # print regions + amount range BEFORE filtering
    regions = sorted({v["Region"] for v in valid})
    print(f"Available regions: {regions}")

    if valid:
        amounts = [v["_amount"] for v in valid]
        print(f"Transaction amount range: {min(amounts):.2f} - {max(amounts):.2f}")
    else:
        print("Transaction amount range: 0.00 - 0.00")

    current = valid
    print(f"Records after validation: {len(current)}")

    # region filter
    if region is not None:
        before = len(current)
        current = [v for v in current if v["Region"] == region]
        removed = before - len(current)
        summary["filtered_by_region"] = removed
        print(f"Records after region filter ({region}): {len(current)}")

    # amount filter
    if min_amount is not None or max_amount is not None:
        before = len(current)

        def ok(v: Dict) -> bool:
            amt = v["_amount"]
            if min_amount is not None and amt < float(min_amount):
                return False
            if max_amount is not None and amt > float(max_amount):
                return False
            return True

        current = [v for v in current if ok(v)]
        removed = before - len(current)
        summary["filtered_by_amount"] = removed
        print(f"Records after amount filter: {len(current)}")

    # remove helper field before returning
    for v in current:
        v.pop("_amount", None)

    summary["final_count"] = len(current)
    return current, invalid, summary

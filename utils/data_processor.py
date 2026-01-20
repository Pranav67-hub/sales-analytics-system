from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Tuple


def _qty(tx: Dict[str, Any]) -> int:
    return int(str(tx.get("Quantity", 0)).replace(",", ""))


def _price(tx: Dict[str, Any]) -> float:
    return float(str(tx.get("UnitPrice", 0)).replace(",", ""))


def _amount(tx: Dict[str, Any]) -> float:
    return _qty(tx) * _price(tx)


# ------------------------------------------------------------
# Task 2.1: Sales Summary Calculator
# ------------------------------------------------------------

def calculate_total_revenue(transactions: List[Dict[str, Any]]) -> float:
    """
    Calculates total revenue from all transactions.
    Expected: single number sum(Quantity * UnitPrice)
    Example: 1545000.50
    """
    total = 0.0
    for tx in transactions:
        total += _amount(tx)
    return round(total, 2)


def region_wise_sales(transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Returns a dict sorted by total_sales (desc).

    Output format per region:
    {
      "North": {
        "total_sales": 450000.0,
        "transaction_count": 15,
        "percentage": 29.13
      },
      ...
    }

    Requirements:
    - total sales per region
    - count transactions per region
    - percentage of total sales
    - sorted by total_sales descending
    """
    total_revenue = calculate_total_revenue(transactions)
    region_totals = defaultdict(float)
    region_counts = defaultdict(int)

    for tx in transactions:
        region = tx.get("Region", "")
        region_totals[region] += _amount(tx)
        region_counts[region] += 1

    rows = []
    for region, tot in region_totals.items():
        pct = (tot / total_revenue * 100.0) if total_revenue else 0.0
        rows.append((region, tot, region_counts[region], pct))

    rows.sort(key=lambda x: x[1], reverse=True)

    out: Dict[str, Dict[str, Any]] = {}
    for region, tot, cnt, pct in rows:
        out[region] = {
            "total_sales": round(tot, 2),
            "transaction_count": cnt,
            "percentage": round(pct, 2),
        }
    return out


def top_selling_products(transactions: List[Dict[str, Any]], n: int = 5) -> List[Tuple[str, int, float]]:
    """
    Finds top n products by total quantity sold.
    Returns list of tuples:
    [
      ("Laptop", 45, 225000.0),  # (ProductName, TotalQuantity, TotalRevenue)
      ("Mouse", 38, 19000.0),
      ...
    ]

    Requirements:
    - aggregate by ProductName
    - total quantity sold
    - total revenue per product
    - sort by TotalQuantity desc
    - return top n
    """
    qty_by_product = defaultdict(int)
    rev_by_product = defaultdict(float)

    for tx in transactions:
        p = tx.get("ProductName", "")
        qty = _qty(tx)
        amt = _amount(tx)
        qty_by_product[p] += qty
        rev_by_product[p] += amt

    rows = [(p, qty_by_product[p], round(rev_by_product[p], 2)) for p in qty_by_product]
    rows.sort(key=lambda x: x[1], reverse=True)
    return rows[:n]


def customer_analysis(transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Analyzes customer purchase patterns.

    Output format:
    {
      "C001": {
        "total_spent": 95000.0,
        "purchase_count": 3,
        "avg_order_value": 31666.67,
        "products_bought": ["Laptop","Mouse","Keyboard"]
      },
      ...
    }

    Requirements:
    - total amount spent per customer
    - number of purchases
    - average order value
    - unique products bought
    - sorted by total_spent descending
    """
    spend = defaultdict(float)
    count = defaultdict(int)
    products = defaultdict(set)

    for tx in transactions:
        c = tx.get("CustomerID", "")
        spend[c] += _amount(tx)
        count[c] += 1
        products[c].add(tx.get("ProductName", ""))

    rows = []
    for c in spend:
        avg = (spend[c] / count[c]) if count[c] else 0.0
        rows.append((c, spend[c], count[c], avg, sorted(products[c])))

    rows.sort(key=lambda x: x[1], reverse=True)

    out: Dict[str, Dict[str, Any]] = {}
    for c, total_spent, purchase_count, avg, prod_list in rows:
        out[c] = {
            "total_spent": round(total_spent, 2),
            "purchase_count": purchase_count,
            "avg_order_value": round(avg, 2),
            "products_bought": prod_list,  # already unique
        }
    return out


# ------------------------------------------------------------
# Task 2.2: Date-based Analysis
# ------------------------------------------------------------

def daily_sales_trend(transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Groups by date and returns chronologically sorted dict.

    Expected format:
    {
      "2024-12-01": {"revenue": 125000.0, "transaction_count": 8, "unique_customers": 6},
      "2024-12-02": {...},
      ...
    }

    Requirements:
    - group by date
    - daily revenue
    - daily transaction count
    - unique customers per day
    - sorted chronologically
    """
    rev = defaultdict(float)
    cnt = defaultdict(int)
    uniq = defaultdict(set)

    for tx in transactions:
        d = tx.get("Date", "")
        rev[d] += _amount(tx)
        cnt[d] += 1
        uniq[d].add(tx.get("CustomerID", ""))

    out: Dict[str, Dict[str, Any]] = {}
    for d in sorted(rev.keys()):
        out[d] = {
            "revenue": round(rev[d], 2),
            "transaction_count": cnt[d],
            "unique_customers": len(uniq[d]),
        }
    return out


def find_peak_sales_day(transactions: List[Dict[str, Any]]) -> Tuple[str, float, int]:
    """
    Identifies the date with the highest revenue.
    Returns: (date, revenue, transaction_count)
    Example: ("2024-12-15", 185000.0, 12)
    """
    daily = daily_sales_trend(transactions)
    if not daily:
        return ("", 0.0, 0)

    # max by revenue; if tie, earliest date wins (stable + deterministic)
    best_date = min(daily.keys())
    best_rev = daily[best_date]["revenue"]
    for d, stats in daily.items():
        if stats["revenue"] > best_rev:
            best_date = d
            best_rev = stats["revenue"]

    return (best_date, float(daily[best_date]["revenue"]), int(daily[best_date]["transaction_count"]))


# ------------------------------------------------------------
# Task 2.3: Product Performance
# ------------------------------------------------------------

def low_performing_products(transactions: List[Dict[str, Any]], threshold: int = 10) -> List[Tuple[str, int, float]]:
    """
    Finds products with total quantity < threshold.

    Expected output format:
    [
      ("Webcam", 4, 12000.0),     # (ProductName, TotalQuantity, TotalRevenue)
      ("Headphones", 7, 10500.0),
      ...
    ]

    Requirements:
    - include total quantity and revenue
    - sort by TotalQuantity ascending
    """
    qty_by_product = defaultdict(int)
    rev_by_product = defaultdict(float)

    for tx in transactions:
        p = tx.get("ProductName", "")
        q = _qty(tx)
        qty_by_product[p] += q
        rev_by_product[p] += _amount(tx)

    rows = []
    for p in qty_by_product:
        total_q = qty_by_product[p]
        if total_q < threshold:
            rows.append((p, total_q, round(rev_by_product[p], 2)))

    rows.sort(key=lambda x: x[1])  # ascending quantity
    return rows

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Tuple

from .file_handler import SalesRecord


def compute_kpis(records: List[SalesRecord]) -> Dict[str, Any]:
    total_orders = len(records)
    total_revenue = sum(r.revenue for r in records)
    avg_order_value = (total_revenue / total_orders) if total_orders else 0.0

    revenue_by_region: Dict[str, float] = defaultdict(float)
    revenue_by_product: Dict[str, float] = defaultdict(float)
    orders_by_customer: Dict[str, int] = defaultdict(int)
    spend_by_customer: Dict[str, float] = defaultdict(float)
    revenue_by_date: Dict[str, float] = defaultdict(float)

    for r in records:
        revenue_by_region[r.region] += r.revenue
        revenue_by_product[r.product_name] += r.revenue
        orders_by_customer[r.customer_id] += 1
        spend_by_customer[r.customer_id] += r.revenue
        revenue_by_date[r.date] += r.revenue

    top_products = sorted(revenue_by_product.items(), key=lambda x: x[1], reverse=True)[:5]
    top_customers = sorted(spend_by_customer.items(), key=lambda x: x[1], reverse=True)[:5]
    repeat_customers_count = sum(1 for _, n in orders_by_customer.items() if n > 1)

    return {
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "avg_order_value": round(avg_order_value, 2),
        "revenue_by_region": {k: round(v, 2) for k, v in sorted(revenue_by_region.items(), key=lambda x: x[1], reverse=True)},
        "top_products_by_revenue": [(p, round(v, 2)) for p, v in top_products],
        "top_customers_by_spend": [(c, round(v, 2)) for c, v in top_customers],
        "repeat_customers_count": repeat_customers_count,
        "daily_revenue": {k: round(v, 2) for k, v in sorted(revenue_by_date.items())},
    }

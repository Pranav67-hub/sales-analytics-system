from __future__ import annotations

import argparse
from pathlib import Path

from utils.file_handler import load_and_clean_sales
from utils.api_client import ProductAPIClient
from utils.analytics import compute_kpis
from utils.report import write_json_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Sales Analytics System")
    parser.add_argument("--input", default="data/sales_data.txt", help="Path to sales data file")
    parser.add_argument("--report", default="reports/report.json", help="Output report path (JSON)")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"ERROR: Input file not found: {args.input}")
        print("Fix: put sales_data.txt inside data/ as data/sales_data.txt OR pass --input <path>")
        return

    records, stats = load_and_clean_sales(args.input)

    # Enrichment via API (safe: failures return {})
    client = ProductAPIClient()
    product_ids = sorted({r.product_id for r in records})
    product_api_snapshot = {pid: client.get_product_info(pid) for pid in product_ids}

    kpis = compute_kpis(records)

    report = {
        "validation": stats,
        "kpis": kpis,
        "product_api_snapshot": product_api_snapshot,
    }

    write_json_report(report, args.report)
    print(f"\nReport written to: {args.report}")


if __name__ == "__main__":
    main()

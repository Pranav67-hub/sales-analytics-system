from __future__ import annotations

import argparse
from pathlib import Path
from utils.file_handler import load_and_clean_sales


def main() -> None:
    parser = argparse.ArgumentParser(description="Sales Analytics System")
    parser.add_argument("--input", default="data/sales_data.txt", help="Path to sales data file")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"ERROR: Input file not found: {args.input}")
        print("Place your sales_data.txt inside a folder named 'data' as data/sales_data.txt")
        return

    load_and_clean_sales(args.input)


if __name__ == "__main__":
    main()


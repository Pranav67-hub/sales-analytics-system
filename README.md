# Sales Analytics System

A small end-to-end sales analytics pipeline:
1) Reads messy pipe-delimited sales transactions (handles non-UTF-8 files)
2) Cleans + validates records based on assignment rules
3) Enriches products using a public product API
4) Computes KPIs and generates a JSON report

## Repo structure (required)
- main.py
- utils/file_handler.py
- README.md

## How to run

### 1) Put the dataset here
Place your raw file at:
- data/sales_data.txt

### 2) Run the pipeline
From the repository root:

```bash
python main.py --input data/sales_data.txt --report reports/report.json

## Quick sanity check
After running, confirm the console prints:
Total records parsed: 80
Invalid records removed: 10
Valid records after cleaning: 70
```
###Module 3 Q3 functions are in utils/data_processor.py

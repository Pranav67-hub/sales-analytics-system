from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def write_json_report(report: Dict[str, Any], out_path: str) -> None:
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report, indent=2), encoding="utf-8")

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class ProductAPIClient:
    """
    Fetches product info from a public API.
    Uses caching + retries so it doesn't break if network/API is flaky.
    """
    base_url: str = "https://dummyjson.com/products"
    timeout_sec: int = 10
    max_retries: int = 2
    backoff_sec: float = 0.5
    cache: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def get_product_info(self, product_id: str) -> Dict[str, Any]:
        if product_id in self.cache:
            return self.cache[product_id]

        numeric = "".join(ch for ch in product_id if ch.isdigit())
        if not numeric:
            self.cache[product_id] = {}
            return {}

        url = f"{self.base_url}/{int(numeric)}"
        req = Request(url, headers={"User-Agent": "sales-analytics-system/1.0"})

        for attempt in range(self.max_retries + 1):
            try:
                with urlopen(req, timeout=self.timeout_sec) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    self.cache[product_id] = data
                    return data
            except (HTTPError, URLError, TimeoutError, ValueError):
                if attempt == self.max_retries:
                    break
                time.sleep(self.backoff_sec * (2 ** attempt))

        self.cache[product_id] = {}
        return {}

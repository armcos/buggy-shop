"""Sales analytics with running statistics."""

from collections import defaultdict
from typing import List, Dict, Optional


class SalesTracker:
    """Track sales and compute running statistics."""

    def __init__(self):
        self._sales: List[Dict] = []
        self._daily_cache: Dict[str, float] = {}

    def record_sale(self, date: str, sku: str, quantity: int, unit_price: float):
        """Record a sale event."""
        self._sales.append({
            "date": date,
            "sku": sku,
            "quantity": quantity,
            "unit_price": unit_price,
            "revenue": quantity * unit_price,
        })
        # Update daily cache
        self._daily_cache[date] = (
            self._daily_cache.get(date, 0) + quantity * unit_price
        )

    def daily_revenue(self, date: str) -> float:
        return self._daily_cache.get(date, 0.0)

    def top_products(self, n: int = 5) -> List[Dict]:
        """Return top N products by total revenue."""
        revenue_by_sku = defaultdict(float)
        qty_by_sku = defaultdict(int)

        for sale in self._sales:
            revenue_by_sku[sale["sku"]] += sale["revenue"]
            qty_by_sku[sale["sku"]] += sale["quantity"]

        ranked = sorted(revenue_by_sku.items(), key=lambda x: x[1], reverse=True)

        return [
            {"sku": sku, "revenue": rev, "units_sold": qty_by_sku[sku]}
            for sku, rev in ranked[:n]
        ]

    def moving_average(self, sku: str, window: int = 7) -> Optional[float]:
        """Compute moving average of daily revenue for a SKU over last N days."""
        sku_sales = [s for s in self._sales if s["sku"] == sku]

        if not sku_sales:
            return None

        daily = defaultdict(float)
        for s in sku_sales:
            daily[s["date"]] += s["revenue"]

        sorted_days = sorted(daily.keys())
        recent = sorted_days[-window:]

        total = sum(daily[d] for d in recent)
        return round(total / window, 2)

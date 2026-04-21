"""Pricing engine with tiered bulk discounts."""

from typing import Dict, List, Tuple


# Tier thresholds: (min_quantity, discount_percentage)
DEFAULT_TIERS: List[Tuple[int, float]] = [
    (50, 15.0),
    (20, 10.0),
    (10, 5.0),
    (1, 0.0),
]


def get_bulk_discount(quantity: int, tiers: List[Tuple[int, float]] = None) -> float:
    """Return the discount percentage for a given quantity.

    Tiers are checked from highest threshold to lowest.
    """
    if tiers is None:
        tiers = DEFAULT_TIERS

    for min_qty, discount in tiers:
        if quantity >= min_qty:
            return discount
    return 0.0


def compute_invoice(items: Dict[str, Tuple[float, int]],
                    tiers: List[Tuple[int, float]] = None) -> Dict:
    """Compute an invoice from a dict of {sku: (unit_price, quantity)}.

    Returns a dict with line items and a grand total.
    """
    result = {"lines": [], "total": 0.0}

    for sku, (price, qty) in items.items():
        discount_pct = get_bulk_discount(qty, tiers)
        discounted = price * (1 - discount_pct / 100)
        line_total = discounted * qty
        result["lines"].append({
            "sku": sku,
            "unit_price": price,
            "quantity": qty,
            "discount_pct": discount_pct,
            "line_total": round(line_total, 2),
        })
        result["total"] += line_total

    result["total"] = round(result["total"], 2)
    return result

"""Inventory management with stock reservation."""

from typing import Dict, Optional
from .models import Product


class InventoryManager:
    """Manages product stock with reservation support."""

    def __init__(self):
        self._products: Dict[str, Product] = {}
        self._reservations: Dict[str, Dict[str, int]] = {}  # order_id -> {sku: qty}

    def register_product(self, product: Product):
        """Register a product in the inventory, keyed by its SKU."""
        self._products[product.sku] = product

    def get_product(self, sku: str) -> Optional[Product]:
        """Look up a product by SKU, returning None if unknown."""
        return self._products.get(sku)

    def available_stock(self, sku: str) -> int:
        """Return stock minus all active reservations."""
        product = self._products.get(sku)
        if not product:
            return 0
        reserved = sum(
            res.get(sku, 0) for res in self._reservations.values()
        )
        return product.stock - reserved

    def reserve(self, order_id: str, sku: str, quantity: int) -> bool:
        """Reserve ``quantity`` units of ``sku`` against ``order_id``.

        Returns True on success, False if insufficient stock is available.
        """
        if self.available_stock(sku) < quantity:
            return False

        if order_id not in self._reservations:
            self._reservations[order_id] = {}

        self._reservations[order_id][sku] = quantity
        return True

    def confirm_order(self, order_id: str):
        """Confirm an order: deduct reserved stock permanently."""
        if order_id not in self._reservations:
            return

        for sku, qty in self._reservations[order_id].items():
            product = self._products.get(sku)
            if product:
                product.stock -= qty

        del self._reservations[order_id]

    def cancel_order(self, order_id: str):
        """Cancel an order: release reserved stock."""
        self._reservations.pop(order_id, None)

    def restock(self, sku: str, quantity: int):
        """Add ``quantity`` units back to on-hand stock for ``sku``."""
        product = self._products.get(sku)
        if product:
            product.stock += quantity

    def low_stock_report(self, threshold: int = 5) -> Dict[str, int]:
        """Return products with available stock below threshold."""
        report = {}
        for sku in self._products:
            avail = self.available_stock(sku)
            if avail < threshold:
                report[sku] = avail
        return report

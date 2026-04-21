"""Product and inventory models for the shop."""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Product:
    name: str
    price: float
    sku: str
    stock: int = 0
    tags: list = field(default_factory=list)

    def apply_discount(self, percentage: float) -> float:
        """Return discounted price."""
        return self.price * (1 - percentage / 100)


@dataclass
class OrderLine:
    product: Product
    quantity: int

    @property
    def subtotal(self) -> float:
        return self.product.price * self.quantity


@dataclass
class Order:
    customer_name: str
    lines: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    _discount_rules: dict = field(default_factory=dict)

    def add_line(self, product: Product, quantity: int):
        self.lines.append(OrderLine(product=product, quantity=quantity))

    def register_discount(self, sku: str, percentage: float):
        """Register a discount rule for a product SKU."""
        self._discount_rules[sku] = percentage

    @property
    def total(self) -> float:
        total = 0.0
        for line in self.lines:
            sku = line.product.sku
            if sku in self._discount_rules:
                pct = self._discount_rules[sku]
                total += line.product.apply_discount(pct) * line.quantity
            else:
                total += line.subtotal
        return round(total, 2)

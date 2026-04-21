"""Main entry point demonstrating the shop system."""

import csv
import os

from .models import Product, Order
from .inventory import InventoryManager
from .pricing import compute_invoice
from .analytics import SalesTracker


def load_sales(tracker: SalesTracker, filepath: str):
    """Load sales records from a CSV file into the tracker."""
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tracker.record_sale(
                date=row["date"],
                sku=row["sku"],
                quantity=int(row["quantity"]),
                unit_price=float(row["unit_price"]),
            )


def run_demo():
    # Setup inventory
    inv = InventoryManager()
    inv.register_product(Product("Wireless Mouse", 29.99, "WM-001", stock=100))
    inv.register_product(Product("Mechanical Keyboard", 89.99, "KB-002", stock=50))
    inv.register_product(Product("USB-C Hub", 49.99, "HB-003", stock=30))

    # Create an order
    order = Order(customer_name="Alice")
    mouse = inv.get_product("WM-001")
    kb = inv.get_product("KB-002")

    order.add_line(mouse, 25)
    order.add_line(kb, 5)
    order.register_discount("WM-001", 10.0)

    print(f"Order total: ${order.total:.2f}")

    # Reserve and confirm
    inv.reserve("ORD-001", "WM-001", 25)
    inv.reserve("ORD-001", "KB-002", 5)
    inv.confirm_order("ORD-001")

    print(f"Mouse stock after order: {inv.available_stock('WM-001')}")
    print(f"Keyboard stock after order: {inv.available_stock('KB-002')}")

    # Compute bulk invoice
    invoice = compute_invoice({
        "WM-001": (29.99, 25),
        "KB-002": (89.99, 5),
        "HB-003": (49.99, 12),
    })
    print(f"\nInvoice total: ${invoice['total']:.2f}")
    for line in invoice["lines"]:
        print(f"  {line['sku']}: {line['quantity']} x ${line['unit_price']:.2f} "
              f"(-{line['discount_pct']}%) = ${line['line_total']:.2f}")

    # Load sales from external data file and run analytics
    tracker = SalesTracker()
    sales_file = os.environ.get(
        "SHOP_SALES_CSV",
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "shop-data", "sales.csv"),
    )
    load_sales(tracker, sales_file)

    avg = tracker.moving_average("WM-001", window=7)
    print(f"\nMouse 7-day moving avg revenue: ${avg}")

    avg_kb = tracker.moving_average("KB-002", window=7)
    print(f"Keyboard 7-day moving avg revenue: ${avg_kb}")

    top = tracker.top_products(3)
    print("\nTop products:")
    for p in top:
        print(f"  {p['sku']}: ${p['revenue']:.2f} ({p['units_sold']} units)")

    # Low stock check
    inv.restock("HB-003", 0)  # no restock
    report = inv.low_stock_report(threshold=35)
    print(f"\nLow stock alerts: {report}")


if __name__ == "__main__":
    run_demo()

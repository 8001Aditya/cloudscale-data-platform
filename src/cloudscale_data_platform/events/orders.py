"""Synthetic retail order event contract and generator."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Any
from uuid import NAMESPACE_URL, uuid5

_CENTS = Decimal("0.01")
_BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)
_PRODUCT_CATALOG = (
    ("SKU-1001", "wireless mouse", Decimal("24.99")),
    ("SKU-1002", "mechanical keyboard", Decimal("89.50")),
    ("SKU-1003", "usb-c hub", Decimal("42.75")),
    ("SKU-1004", "laptop stand", Decimal("37.20")),
    ("SKU-1005", "noise cancelling headphones", Decimal("129.99")),
)
_REGIONS = ("north", "south", "east", "west", "central")
_CHANNELS = ("web", "mobile", "store")


@dataclass(frozen=True)
class Money:
    """Currency amount represented with fixed two-decimal precision."""

    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        object.__setattr__(self, "amount", self.amount.quantize(_CENTS, rounding=ROUND_HALF_UP))

    def to_dict(self) -> dict[str, str]:
        return {"amount": str(self.amount), "currency": self.currency}


@dataclass(frozen=True)
class OrderItem:
    """Line item within a synthetic order."""

    sku: str
    name: str
    quantity: int
    unit_price: Money

    @property
    def line_total(self) -> Money:
        return Money(self.unit_price.amount * self.quantity, self.unit_price.currency)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sku": self.sku,
            "name": self.name,
            "quantity": self.quantity,
            "unit_price": self.unit_price.to_dict(),
            "line_total": self.line_total.to_dict(),
        }


@dataclass(frozen=True)
class OrderCreatedEvent:
    """Versioned event emitted when a retail order is created."""

    event_id: str
    correlation_id: str
    event_type: str
    schema_version: int
    occurred_at: datetime
    order_id: str
    customer_id: str
    region: str
    channel: str
    items: tuple[OrderItem, ...]

    @property
    def event_key(self) -> str:
        return self.order_id

    @property
    def total_amount(self) -> Money:
        total = sum((item.line_total.amount for item in self.items), Decimal("0.00"))
        return Money(total)

    def to_payload(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "correlation_id": self.correlation_id,
            "event_type": self.event_type,
            "schema_version": self.schema_version,
            "occurred_at": self.occurred_at.isoformat().replace("+00:00", "Z"),
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "region": self.region,
            "channel": self.channel,
            "items": [item.to_dict() for item in self.items],
            "total_amount": self.total_amount.to_dict(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_payload(), separators=(",", ":"), sort_keys=True)


def generate_order_created_event(
    sequence_number: int,
    *,
    schema_version: int,
    seed: int,
) -> OrderCreatedEvent:
    """Generate a deterministic synthetic order event."""
    randomizer = random.Random(f"{seed}:{sequence_number}")
    order_id = f"ORD-{sequence_number:012d}"
    occurred_at = _BASE_TIME + timedelta(seconds=sequence_number)
    items = _generate_items(randomizer)

    return OrderCreatedEvent(
        event_id=str(uuid5(NAMESPACE_URL, f"cloudscale:{schema_version}:{seed}:{sequence_number}")),
        correlation_id=str(uuid5(NAMESPACE_URL, f"cloudscale:order-correlation:{seed}:{order_id}")),
        event_type="order.created",
        schema_version=schema_version,
        occurred_at=occurred_at,
        order_id=order_id,
        customer_id=f"CUST-{randomizer.randint(1, 50_000):08d}",
        region=randomizer.choice(_REGIONS),
        channel=randomizer.choice(_CHANNELS),
        items=items,
    )


def _generate_items(randomizer: random.Random) -> tuple[OrderItem, ...]:
    item_count = randomizer.randint(1, 4)
    products = randomizer.sample(_PRODUCT_CATALOG, item_count)
    return tuple(
        OrderItem(
            sku=sku,
            name=name,
            quantity=randomizer.randint(1, 5),
            unit_price=Money(price),
        )
        for sku, name, price in products
    )

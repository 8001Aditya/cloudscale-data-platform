"""Event contracts used by the CloudScale data platform."""

from cloudscale_data_platform.events.orders import (
    Money,
    OrderCreatedEvent,
    OrderItem,
    generate_order_created_event,
)

__all__ = [
    "Money",
    "OrderCreatedEvent",
    "OrderItem",
    "generate_order_created_event",
]

from __future__ import annotations

import json
from decimal import Decimal

from cloudscale_data_platform.events import Money, generate_order_created_event


def test_order_event_generation_is_deterministic() -> None:
    first_event = generate_order_created_event(1, schema_version=1, seed=42)
    second_event = generate_order_created_event(1, schema_version=1, seed=42)

    assert first_event.to_payload() == second_event.to_payload()
    assert first_event.event_key == "ORD-000000000001"


def test_order_event_payload_is_kafka_friendly_json() -> None:
    event = generate_order_created_event(7, schema_version=1, seed=8001)
    payload = json.loads(event.to_json())

    assert payload["event_type"] == "order.created"
    assert payload["correlation_id"]
    assert payload["correlation_id"] != payload["event_id"]
    assert payload["schema_version"] == 1
    assert payload["occurred_at"].endswith("Z")
    assert payload["order_id"] == event.event_key
    assert payload["items"]
    assert Decimal(payload["total_amount"]["amount"]) > Decimal("0.00")


def test_money_amounts_are_rounded_to_two_decimal_places() -> None:
    money = Money(Decimal("10.125"))

    assert money.to_dict() == {"amount": "10.13", "currency": "USD"}

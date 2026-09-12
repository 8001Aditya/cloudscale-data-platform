from __future__ import annotations

import json

from cloudscale_data_platform.producer.cli import main


def test_producer_cli_writes_requested_events(tmp_path, monkeypatch) -> None:
    output_path = tmp_path / "orders.jsonl"
    monkeypatch.setenv("CLOUDSCALE_EVENT_SCHEMA_VERSION", "2")

    exit_code = main(["--output", str(output_path), "--count", "3", "--seed", "99"])

    lines = output_path.read_text(encoding="utf-8").splitlines()
    payloads = [json.loads(line) for line in lines]
    assert exit_code == 0
    assert len(payloads) == 3
    assert [payload["schema_version"] for payload in payloads] == [2, 2, 2]
    assert [payload["order_id"] for payload in payloads] == [
        "ORD-000000000001",
        "ORD-000000000002",
        "ORD-000000000003",
    ]

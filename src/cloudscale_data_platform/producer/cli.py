"""Command-line producer for synthetic retail order events."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from cloudscale_data_platform.config import ApplicationConfig
from cloudscale_data_platform.events import generate_order_created_event


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    config = ApplicationConfig.from_environment()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as output_file:
        for sequence_number in range(args.start_sequence, args.start_sequence + args.count):
            event = generate_order_created_event(
                sequence_number,
                schema_version=config.event_schema_version,
                seed=args.seed,
            )
            output_file.write(event.to_json())
            output_file.write("\n")

    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cloudscale-produce-orders",
        description="Generate synthetic retail order events as newline-delimited JSON.",
    )
    parser.add_argument(
        "--output",
        default="data/local/raw/orders.jsonl",
        help="Path to the JSONL file to write.",
    )
    parser.add_argument(
        "--count",
        type=_positive_int,
        default=10,
        help="Number of events to generate.",
    )
    parser.add_argument(
        "--start-sequence",
        type=_positive_int,
        default=1,
        help="First order sequence number to generate.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=8001,
        help="Deterministic generator seed.",
    )
    return parser


def _positive_int(value: str) -> int:
    parsed_value = int(value)
    if parsed_value < 1:
        raise argparse.ArgumentTypeError("value must be a positive integer")
    return parsed_value


if __name__ == "__main__":
    raise SystemExit(main())

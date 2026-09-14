"""Command-line interface for ADLS raw ingestion."""

from __future__ import annotations

import argparse
from pathlib import Path

from cloudscale_data_platform.ingestion.adls import AdlsRawIngester


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Upload a local raw file to Azure Data Lake Storage Gen2."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Local file to upload.",
    )

    parser.add_argument(
        "--storage-account",
        default="cloudscaledevdata",
        help="Azure Storage Account name.",
    )

    parser.add_argument(
        "--filesystem",
        default="datalake",
        help="ADLS Gen2 filesystem/container name.",
    )

    args = parser.parse_args()

    ingester = AdlsRawIngester(
        storage_account=args.storage_account,
        filesystem=args.filesystem,
    )

    destination = ingester.upload_raw_file(
        Path(args.input),
    )

    print(f"Uploaded: {destination}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

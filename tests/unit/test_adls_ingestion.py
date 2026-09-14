"""Unit tests for Azure Data Lake Storage Gen2 raw ingestion."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from cloudscale_data_platform.ingestion.adls import AdlsRawIngester


class FakeDirectoryClient:
    """Fake ADLS directory client used for unit tests."""

    def __init__(self) -> None:
        self.created = False

    def create_directory(self) -> None:
        self.created = True


class FakeFileClient:
    """Fake ADLS file client used for unit tests."""

    def __init__(self) -> None:
        self.created = False
        self.appended_data: bytes | None = None
        self.appended_offset: int | None = None
        self.appended_length: int | None = None
        self.flushed_position: int | None = None

    def create_file(self) -> None:
        self.created = True

    def append_data(
        self,
        *,
        data: bytes,
        offset: int,
        length: int,
    ) -> None:
        self.appended_data = data
        self.appended_offset = offset
        self.appended_length = length

    def flush_data(self, *, offset: int) -> None:
        self.flushed_position = offset


class FakeFileSystemClient:
    """Fake ADLS filesystem client used for unit tests."""

    def __init__(self) -> None:
        self.directories: dict[str, FakeDirectoryClient] = {}
        self.file_client = FakeFileClient()

    def get_directory_client(
        self,
        directory: str,
    ) -> FakeDirectoryClient:
        if directory not in self.directories:
            self.directories[directory] = FakeDirectoryClient()

        return self.directories[directory]

    def get_file_client(
        self,
        _file_path: str,
    ) -> FakeFileClient:
        return self.file_client


def test_upload_raw_file_creates_partitioned_destination(
    tmp_path: Path,
) -> None:
    """Raw files should be uploaded into a date-partitioned directory."""

    input_file = tmp_path / "orders.jsonl"
    input_data = b'{"order_id":"ORD-001"}\n'
    input_file.write_bytes(input_data)

    fake_filesystem = FakeFileSystemClient()

    ingester = object.__new__(AdlsRawIngester)
    ingester.file_system_client = fake_filesystem

    ingest_time = datetime(
        2026,
        9,
        14,
        14,
        30,
        0,
        tzinfo=UTC,
    )

    destination = ingester.upload_raw_file(
        input_file,
        ingest_time=ingest_time,
    )

    assert destination.startswith("raw/orders/ingest_date=2026-09-14/orders_")

    assert destination.endswith(".jsonl")

    # Verify the directory hierarchy was created.
    assert "raw" in fake_filesystem.directories
    assert "raw/orders" in fake_filesystem.directories
    assert "raw/orders/ingest_date=2026-09-14" in fake_filesystem.directories

    assert fake_filesystem.directories["raw"].created is True
    assert fake_filesystem.directories["raw/orders"].created is True
    assert fake_filesystem.directories["raw/orders/ingest_date=2026-09-14"].created is True

    # Verify the file upload lifecycle.
    file_client = fake_filesystem.file_client

    assert file_client.created is True
    assert file_client.appended_data == input_data
    assert file_client.appended_offset == 0
    assert file_client.appended_length == len(input_data)
    assert file_client.flushed_position == len(input_data)


def test_upload_raw_file_raises_for_missing_file(
    tmp_path: Path,
) -> None:
    """A missing input file should raise FileNotFoundError."""

    missing_file = tmp_path / "missing.jsonl"

    fake_filesystem = FakeFileSystemClient()

    ingester = object.__new__(AdlsRawIngester)
    ingester.file_system_client = fake_filesystem

    with pytest.raises(FileNotFoundError, match="Input file does not exist"):
        ingester.upload_raw_file(missing_file)

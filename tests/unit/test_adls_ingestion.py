from datetime import UTC, datetime
from pathlib import Path

from cloudscale_data_platform.ingestion.adls import AdlsRawIngester


class FakeDirectoryClient:
    def __init__(self) -> None:
        self.created = False

    def create_directory(self) -> None:
        self.created = True


class FakeFileClient:
    def __init__(self) -> None:
        self.uploaded_data = None
        self.overwrite = None

    def upload_data(self, data, *, overwrite: bool) -> None:
        self.uploaded_data = data.read()
        self.overwrite = overwrite


class FakeFileSystemClient:
    def __init__(self) -> None:
        self.requested_directory = None
        self.requested_path = None
        self.directory_client = FakeDirectoryClient()
        self.file_client = FakeFileClient()

    def get_directory_client(
        self,
        path: str,
    ) -> FakeDirectoryClient:
        self.requested_directory = path
        return self.directory_client

    def get_file_client(self, path: str) -> FakeFileClient:
        self.requested_path = path
        return self.file_client


def test_upload_raw_file_creates_partitioned_destination(
    tmp_path: Path,
) -> None:
    input_file = tmp_path / "orders.jsonl"
    input_file.write_bytes(b'{"order_id":"ORD-001"}\n')

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

    expected_directory = "raw/orders/ingest_date=2026-09-14"

    assert fake_filesystem.requested_directory == expected_directory
    assert fake_filesystem.directory_client.created is True

    assert destination.startswith("raw/orders/ingest_date=2026-09-14/orders_20260914T143000Z_")
    assert destination.endswith(".jsonl")

    assert fake_filesystem.requested_path == destination
    assert fake_filesystem.file_client.uploaded_data == (b'{"order_id":"ORD-001"}\n')
    assert fake_filesystem.file_client.overwrite is False


def test_upload_raw_file_raises_for_missing_file(
    tmp_path: Path,
) -> None:
    missing_file = tmp_path / "missing.jsonl"

    ingester = object.__new__(AdlsRawIngester)
    ingester.file_system_client = FakeFileSystemClient()

    try:
        ingester.upload_raw_file(missing_file)
    except FileNotFoundError as exc:
        assert "Input file does not exist" in str(exc)
    else:
        raise AssertionError("Expected FileNotFoundError")

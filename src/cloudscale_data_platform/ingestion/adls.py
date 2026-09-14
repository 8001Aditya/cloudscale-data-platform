"""Azure Data Lake Storage Gen2 raw ingestion."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from azure.core.exceptions import ResourceExistsError
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient


class AdlsRawIngester:
    """Upload local raw files into an ADLS Gen2 raw zone."""

    def __init__(
        self,
        *,
        storage_account: str,
        filesystem: str = "datalake",
        credential: DefaultAzureCredential | None = None,
    ) -> None:
        self.storage_account = storage_account
        self.filesystem = filesystem

        account_url = f"https://{storage_account}.dfs.core.windows.net"

        self.credential = credential or DefaultAzureCredential()

        self.service_client = DataLakeServiceClient(
            account_url=account_url,
            credential=self.credential,
        )

        self.file_system_client = self.service_client.get_file_system_client(filesystem)

    def upload_raw_file(
        self,
        local_file: Path,
        *,
        entity: str = "orders",
        ingest_time: datetime | None = None,
    ) -> str:
        """Upload a local file into the partitioned raw zone."""

        if not local_file.is_file():
            raise FileNotFoundError(f"Input file does not exist: {local_file}")

        ingest_time = ingest_time or datetime.now(UTC)
        ingest_date = ingest_time.strftime("%Y-%m-%d")

        unique_id = uuid4().hex[:12]

        destination_directory = f"raw/{entity}/ingest_date={ingest_date}"

        destination_file = (
            f"{destination_directory}/"
            f"{local_file.stem}_{ingest_time.strftime('%Y%m%dT%H%M%SZ')}"
            f"_{unique_id}{local_file.suffix}"
        )

        # Create the directory hierarchy one level at a time.
        directory_parts = destination_directory.split("/")
        current_directory = ""

        for part in directory_parts:
            current_directory = f"{current_directory}/{part}" if current_directory else part

            directory_client = self.file_system_client.get_directory_client(current_directory)

            try:
                directory_client.create_directory()
            except ResourceExistsError:
                pass

        file_client = self.file_system_client.get_file_client(destination_file)

        # Create the file explicitly, then append and flush the data.
        file_client.create_file()

        with local_file.open("rb") as source_file:
            data = source_file.read()

        if data:
            file_client.append_data(
                data=data,
                offset=0,
                length=len(data),
            )

            file_client.flush_data(
                offset=len(data),
            )

        return destination_file

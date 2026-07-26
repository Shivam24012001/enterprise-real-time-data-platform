from enterprise_platform.ingestion.downloader import Downloader
from enterprise_platform.ingestion.results import IngestionResult
from enterprise_platform.storage.minio_client import MinIOClient
from enterprise_platform.storage.path_builder import PathBuilder
from enterprise_platform.storage.uploader import Uploader


class IngestionService:

    def __init__(self, api_config, environment):
        self.api_config = api_config
        self.environment = environment

        self.minio_client = MinIOClient(environment.minio)
        self.downloader = Downloader(api_config)
        self.path_builder = PathBuilder()
        self.uploader = Uploader(self.minio_client)

    def run(self) -> IngestionResult:

        api = self.api_config
        env = self.environment

        records = self.downloader.download()

        object_key = self.path_builder.build_object_key(
            api_name=api.name,
            endpoint=api.endpoint,
        )

        uploaded_path = self.uploader.upload_json(
            bucket_name=env.minio.bucket,
            object_key=object_key,
            data=records,
        )

        return IngestionResult(
            api_name=api.name,
            endpoint=api.endpoint,
            record_count=len(records),
            bucket_name=env.minio.bucket,
            object_key=uploaded_path,
        )

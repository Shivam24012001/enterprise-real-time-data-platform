from minio import Minio

from enterprise_platform.ingestion.models import MinIOConfig


class MinIOClient:

    def __init__(self, config: MinIOConfig) -> None:
        self.config = config
        self.client = Minio(
            endpoint=config.endpoint,
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=False,
        )

    def get_client(self) -> Minio:
        """
        Returns the initialized MinIO client.
        """
        return self.client

    def bucket_exists(self, bucket_name: str) -> bool:
        """
        Check whether a bucket already exists.
        """
        return self.client.bucket_exists(bucket_name)

    def create_bucket(self, bucket_name: str) -> None:
        """
        Create the bucket only if it doesn't already exist.
        """
        if not self.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created successfully.")
        else:
            print(f"Bucket '{bucket_name}' already exists.")

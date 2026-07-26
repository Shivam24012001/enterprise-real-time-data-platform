import io
import json

from enterprise_platform.storage.minio_client import MinIOClient


class Uploader:
    """upload json data in MinIO"""

    def __init__(self, minio_client: MinIOClient):
        self.client = minio_client.get_client()

    def upload_json(
        self,
        bucket_name: str,
        object_key: str,
        data: list | dict,
    ) -> str:

        json_data = json.dumps(data, indent=2)

        json_bytes = json_data.encode("utf-8")

        buffer = io.BytesIO(json_bytes)

        self.client.put_object(
            bucket_name=bucket_name,
            object_name=object_key,
            data=buffer,
            length=len(json_bytes),
            content_type="application/json",
        )

        return object_key

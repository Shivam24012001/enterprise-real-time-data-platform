from enterprise_platform.ingestion.config_loader import ConfigLoader
from enterprise_platform.storage.minio_client import MinIOClient

print("Loading configuration...")

loader = ConfigLoader()

env_config = loader.load_environment()

print("Creating MinIO client...")

minio_client = MinIOClient(env_config.minio)

print("Creating bucket if needed...")

minio_client.create_bucket(env_config.minio.bucket)

print("Checking connection...")

client = minio_client.get_client()

buckets = client.list_buckets()

print()

print("Available Buckets")

for bucket in buckets:
    print(f"- {bucket.name}")

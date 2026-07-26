from datetime import datetime

from pydantic import BaseModel, Field

# ==========================================================
# API Configuration Models
# ==========================================================


class APIConfig(BaseModel):
    """
    Configuration for a single API.
    """

    name: str
    base_url: str
    endpoint: str
    method: str = "GET"
    enabled: bool = True


class APICollection(BaseModel):
    """
    Collection of API configurations.
    """

    apis: list[APIConfig]


# ==========================================================
# MinIO Configuration
# ==========================================================


class MinIOConfig(BaseModel):
    """
    MinIO connection configuration.
    """

    endpoint: str
    access_key: str
    secret_key: str
    bucket: str


# ==========================================================
# Environment Configuration
# ==========================================================


class EnvironmentConfig(BaseModel):
    """
    Environment configuration.
    """

    environment: str
    minio: MinIOConfig


# ==========================================================
# Ingestion Result
# ==========================================================


class IngestionResult(BaseModel):
    """
    Metadata returned after a successful ingestion.

    This model is reused by:
    - Logging
    - Monitoring
    - Audit Tables
    - Airflow
    - API Responses
    """

    api_name: str = Field(description="Name of the source API.")

    endpoint: str = Field(description="API endpoint that was ingested.")

    record_count: int = Field(description="Number of records downloaded.")

    bucket_name: str = Field(description="Destination MinIO bucket.")

    object_key: str = Field(description="Object key where the data was uploaded.")

    ingestion_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when ingestion completed.",
    )

    status: str = Field(default="SUCCESS", description="Status of the ingestion.")

    execution_time_seconds: float | None = Field(
        default=None, description="Pipeline execution time."
    )

    file_size_bytes: int | None = Field(default=None, description="Uploaded file size.")

    error_message: str | None = Field(
        default=None, description="Error message if ingestion fails."
    )

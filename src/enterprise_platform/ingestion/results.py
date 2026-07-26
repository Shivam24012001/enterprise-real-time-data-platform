from datetime import datetime

from pydantic import BaseModel, Field


class IngestionResult(BaseModel):
    api_name: str
    endpoint: str
    record_count: int
    bucket_name: str
    object_key: str

    ingestion_timestamp: datetime = Field(default_factory=datetime.utcnow)

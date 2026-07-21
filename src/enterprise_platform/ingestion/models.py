from pydantic import BaseModel


class APIConfig(BaseModel):
    name: str
    enabled: bool
    base_url: str
    endpoint: str
    method: str
    timeout: int
    retries: int
    output_format: str
    landing_folder: str


class APICollection(BaseModel):
    apis: list[APIConfig]


class MinIOConfig(BaseModel):
    endpoint: str
    access_key: str
    secret_key: str
    bucket: str


class PostgresCofig(BaseModel):
    host: str
    port: int
    database: str
    user: str
    password: str


class EnvironmentConfig(BaseModel):
    environment: str
    log_level: str
    minio: MinIOConfig
    postgres: PostgresCofig

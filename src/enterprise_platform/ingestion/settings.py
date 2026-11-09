from pydantic_settings import BaseSettings, SettingsConfigDict


class Secrets(BaseSettings):
    """Credentials read from environment variables or a local .env file.

    Never put these values in YAML, and never commit .env.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    minio_root_user: str
    minio_root_password: str
    postgres_user: str
    postgres_password: str

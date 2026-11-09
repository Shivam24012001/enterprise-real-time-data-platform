from pathlib import Path

from enterprise_platform.ingestion.config_loader import ConfigLoader
from enterprise_platform.ingestion.settings import Secrets

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "configs"


def test_dev_yaml_has_no_secrets():
    text = (CONFIG_DIR / "environments" / "dev.yaml").read_text()

    for word in ("password", "secret_key", "access_key"):
        assert word not in text, f"'{word}' found in dev.yaml; secrets belong in .env"


def test_secrets_come_from_settings_not_yaml():
    secrets = Secrets(
        minio_root_user="test-user",
        minio_root_password="test-pass",
        postgres_user="pg-user",
        postgres_password="pg-pass",
    )

    config = ConfigLoader(config_directory=str(CONFIG_DIR)).load_environment(
        "dev", secrets=secrets
    )

    assert config.minio.access_key == "test-user"
    assert config.minio.secret_key == "test-pass"
    assert config.postgres.password == "pg-pass"

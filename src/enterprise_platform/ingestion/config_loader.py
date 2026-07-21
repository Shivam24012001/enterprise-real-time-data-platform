from pathlib import Path

import yaml

from enterprise_platform.ingestion.models import APICollection, EnvironmentConfig


class ConfigLoader:
    """
    Loads and validates YAML configuration files.
    """

    def __init__(self, config_directory: str = "configs") -> None:
        self.config_directory = Path(config_directory)

    def load_api_config(self) -> APICollection:
        api_file = self.config_directory / "apis" / "apis.yaml"

        with api_file.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        return APICollection(**data)

    def load_environment(
        self,
        environment: str = "dev",
    ) -> EnvironmentConfig:

        env_file = self.config_directory / "environments" / f"{environment}.yaml"

        with env_file.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        return EnvironmentConfig(**data)

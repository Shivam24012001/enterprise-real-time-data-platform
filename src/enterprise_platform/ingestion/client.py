from typing import Any

import requests

from enterprise_platform.ingestion.models import APIConfig


class APIClient:
    """
    Generic HTTP client for REST APIs.
    """

    def __init__(self, config: APIConfig) -> None:
        self.config = config
        self.base_url = config.base_url.rstrip("/")
        self.timeout = config.timeout

    def request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}{endpoint}"

        response = requests.request(
            method=method, url=url, timeout=self.timeout, **kwargs
        )
        response.raise_for_status()
        return response.json()

    def get(self) -> Any:
        return self.request(
            method="GET",
            endpoint=self.config.endpoint,
        )

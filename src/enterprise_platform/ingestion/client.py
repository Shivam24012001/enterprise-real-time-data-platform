from typing import Any

import requests

from enterprise_platform.ingestion.models import APIConfig
from enterprise_platform.ingestion.retry import RetryPolicy


class APIClient:
    """Generic HTTP client for REST APIs, with retries on transient errors."""

    def __init__(
        self, config: APIConfig, retry_policy: RetryPolicy | None = None
    ) -> None:
        self.config = config
        self.base_url = config.base_url.rstrip("/")
        self.timeout = config.timeout
        self.retry_policy = retry_policy or RetryPolicy(retries=config.retries)

    def request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        """Send an HTTP request and return the JSON response.

        Timeouts, connection errors, 429 and 5xx are retried with backoff,
        `config.retries` times; other errors are raised at once.
        """
        url = f"{self.base_url}{endpoint}"

        def send() -> Any:
            response = requests.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs,
            )
            response.raise_for_status()
            return response.json()

        return self.retry_policy.run(send, description=f"{method} {url}")

    def get(self, **kwargs: Any) -> Any:
        """Perform a GET request on the configured endpoint."""
        return self.request(method="GET", endpoint=self.config.endpoint, **kwargs)

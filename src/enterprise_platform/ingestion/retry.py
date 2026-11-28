import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

import requests
from loguru import logger

T = TypeVar("T")


def is_retryable(error: Exception) -> bool:
    """True for errors a later attempt may fix.

    Retried: timeouts, dropped connections, 429 Too Many Requests and any 5xx.
    Not retried: other 4xx such as 400, 401, 403 and 404; the request itself is
    wrong, so sending it again gives the same answer.
    """
    if isinstance(error, requests.Timeout | requests.ConnectionError):
        return True
    if isinstance(error, requests.HTTPError) and error.response is not None:
        status = error.response.status_code
        return status == 429 or 500 <= status <= 599
    return False


def retry_after_seconds(error: Exception) -> float | None:
    """Seconds asked for by a Retry-After header, if the server sent one.

    Only the number-of-seconds form is used; the HTTP-date form falls back to
    the normal backoff.
    """
    response = getattr(error, "response", None)
    if response is None:
        return None
    value = response.headers.get("Retry-After")
    if value is None:
        return None
    try:
        return max(float(value), 0.0)
    except ValueError:
        return None


@dataclass(frozen=True)
class RetryPolicy:
    """Retry a call on transient HTTP errors, with exponential backoff and jitter.

    retries=3 means up to 4 attempts, waiting about 1 s, 2 s and 4 s in between.
    Jitter adds up to `jitter` seconds at random to each wait, so many clients
    that failed together do not all retry at the same instant.
    Use it for idempotent requests such as GET; retrying a POST can duplicate work.
    """

    retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    jitter: float = 0.5
    sleep: Callable[[float], None] = time.sleep
    random_fn: Callable[[], float] = random.random

    def __post_init__(self) -> None:
        if self.retries < 0:
            raise ValueError(f"retries must be 0 or more, got {self.retries}")

    def delay_for(self, attempt: int, error: Exception) -> float:
        """Seconds to wait after failed attempt number `attempt` (1-based)."""
        server_hint = retry_after_seconds(error)
        if server_hint is not None:
            return min(server_hint, self.max_delay)
        backoff = self.base_delay * 2 ** (attempt - 1)
        return min(backoff + self.jitter * self.random_fn(), self.max_delay)

    def run(self, call: Callable[[], T], description: str = "request") -> T:
        """Run `call`, retrying transient errors; re-raise the last error otherwise."""
        attempts = self.retries + 1
        for attempt in range(1, attempts + 1):
            try:
                return call()
            except requests.RequestException as error:
                if not is_retryable(error):
                    logger.error(
                        "{} failed with a non-retryable error: {}", description, error
                    )
                    raise
                if attempt == attempts:
                    logger.error(
                        "{} failed after {} attempts: {}", description, attempts, error
                    )
                    raise
                wait = self.delay_for(attempt, error)
                logger.warning(
                    "{} failed on attempt {}/{} ({}); retrying in {:.1f}s",
                    description,
                    attempt,
                    attempts,
                    error,
                    wait,
                )
                self.sleep(wait)
        raise RuntimeError("retry loop ended without a result")  # unreachable

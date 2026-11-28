import json

import pytest
import requests

from enterprise_platform.ingestion.client import APIClient
from enterprise_platform.ingestion.models import APIConfig
from enterprise_platform.ingestion.retry import RetryPolicy


def make_config(retries: int = 3) -> APIConfig:
    return APIConfig(
        name="test-api",
        enabled=True,
        base_url="https://api.test",
        endpoint="/posts",
        method="GET",
        timeout=5,
        retries=retries,
        output_format="json",
        landing_folder="raw/test",
    )


def make_response(status: int, body=None, headers=None) -> requests.Response:
    response = requests.Response()
    response.status_code = status
    response._content = json.dumps(body if body is not None else {}).encode()
    response.headers.update(headers or {})
    response.url = "https://api.test/posts"
    return response


class FakeServer:
    """Stands in for requests.request: returns or raises the given outcomes in order."""

    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    def __call__(self, **kwargs):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


@pytest.fixture
def sleeps():
    """Records each wait instead of really sleeping."""
    return []


def client_with(sleeps, retries: int = 3) -> APIClient:
    policy = RetryPolicy(retries=retries, jitter=0, sleep=sleeps.append)
    return APIClient(make_config(retries), retry_policy=policy)


def test_transient_503s_are_retried_until_success(monkeypatch, sleeps):
    server = FakeServer(
        make_response(503), make_response(503), make_response(200, [{"id": 1}])
    )
    monkeypatch.setattr(requests, "request", server)

    result = client_with(sleeps).get()

    assert result == [{"id": 1}]
    assert server.calls == 3
    assert sleeps == [1.0, 2.0]


def test_gives_up_after_configured_retries(monkeypatch, sleeps):
    server = FakeServer(*[make_response(503) for _ in range(4)])
    monkeypatch.setattr(requests, "request", server)

    with pytest.raises(requests.HTTPError, match="503"):
        client_with(sleeps).get()

    assert server.calls == 4  # 1 attempt + 3 retries
    assert sleeps == [1.0, 2.0, 4.0]


def test_client_error_fails_at_once(monkeypatch, sleeps):
    server = FakeServer(make_response(404))
    monkeypatch.setattr(requests, "request", server)

    with pytest.raises(requests.HTTPError, match="404"):
        client_with(sleeps).get()

    assert server.calls == 1
    assert sleeps == []


@pytest.mark.parametrize(
    "error", [requests.Timeout("slow"), requests.ConnectionError("down")]
)
def test_network_errors_are_retried(monkeypatch, sleeps, error):
    server = FakeServer(error, error, make_response(200, {"ok": True}))
    monkeypatch.setattr(requests, "request", server)

    assert client_with(sleeps).get() == {"ok": True}
    assert server.calls == 3


def test_retry_after_header_is_respected(monkeypatch, sleeps):
    server = FakeServer(
        make_response(429, headers={"Retry-After": "7"}), make_response(200, [])
    )
    monkeypatch.setattr(requests, "request", server)

    client_with(sleeps).get()

    assert sleeps == [7.0]


def test_zero_retries_means_one_attempt(monkeypatch, sleeps):
    server = FakeServer(make_response(503))
    monkeypatch.setattr(requests, "request", server)

    with pytest.raises(requests.HTTPError):
        client_with(sleeps, retries=0).get()

    assert server.calls == 1


def test_retries_come_from_config():
    assert APIClient(make_config(retries=5)).retry_policy.retries == 5


def test_jitter_and_max_delay():
    policy = RetryPolicy(jitter=0.5, max_delay=30, random_fn=lambda: 1.0)
    error = requests.Timeout()

    assert policy.delay_for(2, error) == 2.5  # 2 s backoff + 0.5 s jitter
    assert policy.delay_for(10, error) == 30  # capped at max_delay


def test_negative_retries_rejected():
    with pytest.raises(ValueError, match="retries must be 0 or more"):
        RetryPolicy(retries=-1)

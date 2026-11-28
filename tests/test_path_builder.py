from datetime import UTC, datetime

import pytest

from enterprise_platform.storage import path_builder
from enterprise_platform.storage.path_builder import PathBuilder

FIXED_NOW = datetime(2026, 7, 4, 9, 5, 7, tzinfo=UTC)


class FrozenDatetime(datetime):
    """datetime whose now() always returns FIXED_NOW and remembers the tz asked for."""

    requested_tz = None

    @classmethod
    def now(cls, tz=None):
        cls.requested_tz = tz
        return FIXED_NOW


@pytest.fixture(autouse=True)
def frozen_clock(monkeypatch):
    monkeypatch.setattr(path_builder, "datetime", FrozenDatetime)


def test_key_has_layer_api_endpoint_and_zero_padded_date_partitions():
    key = PathBuilder().build_object_key("jsonplaceholder", "/posts")

    assert key == (
        "raw/jsonplaceholder/posts/year=2026/month=07/day=04/posts_20260704_090507.json"
    )


@pytest.mark.parametrize("endpoint", ["/posts", "posts", "posts/", "//posts//"])
def test_slashes_around_the_endpoint_are_stripped(endpoint):
    key = PathBuilder().build_object_key("api", endpoint)

    assert key.startswith("raw/api/posts/year=2026/")
    assert key.endswith("/posts_20260704_090507.json")


def test_extension_is_applied():
    key = PathBuilder().build_object_key("api", "/posts", extension="jsonl")

    assert key.endswith("posts_20260704_090507.jsonl")


def test_layer_is_configurable():
    key = PathBuilder(layer="quarantine").build_object_key("api", "/posts")

    assert key.startswith("quarantine/api/posts/")


def test_partitions_use_utc_time():
    PathBuilder().build_object_key("api", "/posts")

    assert FrozenDatetime.requested_tz is UTC


def test_nested_endpoint_gives_a_flat_file_name():
    key = PathBuilder().build_object_key("api", "/users/1/posts")

    assert key == (
        "raw/api/users/1/posts/year=2026/month=07/day=04/users_1_posts_20260704_090507.json"
    )

from datetime import UTC, datetime


class PathBuilder:
    """Build object keys for the data lake."""

    def __init__(self, layer: str = "raw") -> None:
        self.layer = layer

    def build_object_key(
        self, api_name: str, endpoint: str, extension: str = "json"
    ) -> str:
        """Generate a date-partitioned object key, using UTC time.

        Example:
            raw/jsonplaceholder/posts/year=2026/month=07/day=24/posts_20260724_214530.json

        Slashes around the endpoint are stripped; slashes inside it become folders
        in the path and underscores in the file name, so the file name stays flat.
        """
        now = datetime.now(UTC)
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        timestamp = now.strftime("%Y%m%d_%H%M%S")

        endpoint = endpoint.strip("/")
        file_stem = endpoint.replace("/", "_")
        return (
            f"{self.layer}/"
            f"{api_name}/"
            f"{endpoint}/"
            f"year={year}/"
            f"month={month}/"
            f"day={day}/"
            f"{file_stem}_{timestamp}.{extension}"
        )

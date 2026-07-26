from datetime import datetime


class PathBuilder:
    """build object key for the enterprise data lake"""

    def __init__(self, layer: str = "raw") -> None:
        self.layer = layer

    def build_object_key(
        self, api_name: str, endpoint: str, extension: str = "json"
    ) -> str:
        """Generate a partitioned object key
        Example:
        raw/jsonplaceholder/posts/year=2026/month=07/day=24/posts_20260724_214530.json
        """
        now = datetime.utcnow()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        timestamp = now.strftime("%Y%m%d_%H%M%S")

        endpoint = endpoint.strip("/")
        object_key = (
            f"{self.layer}/"
            f"{api_name}/"
            f"{endpoint}/"
            f"year={year}/"
            f"month={month}/"
            f"day={day}/"
            f"{endpoint}_{timestamp}.{extension}"
        )
        return object_key

"""Manual check: watch the client retry a real 503 from httpbin.org.

Run: python scripts/demo_retry.py
Expect 3 warnings (waits of about 1, 2 and 4 s), then a final error.
"""

import requests

from enterprise_platform.ingestion.client import APIClient
from enterprise_platform.ingestion.models import APIConfig

config = APIConfig(
    name="httpbin",
    enabled=True,
    base_url="https://httpbin.org",
    endpoint="/status/503",
    method="GET",
    timeout=10,
    retries=3,
    output_format="json",
    landing_folder="raw/httpbin",
)

try:
    APIClient(config).get()
except requests.RequestException as error:
    print(f"Gave up as expected: {error}")

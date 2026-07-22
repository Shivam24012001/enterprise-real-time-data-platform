from enterprise_platform.ingestion.client import APIClient
from enterprise_platform.ingestion.models import APIConfig


class Downloader:
    """download data from configured apis"""

    def __init__(self, api_config: APIConfig) -> None:
        self.client = APIClient(api_config)

    def download(self):
        return self.client.get()

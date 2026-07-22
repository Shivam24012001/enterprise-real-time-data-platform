from enterprise_platform.ingestion.config_loader import ConfigLoader
from enterprise_platform.ingestion.downloader import Downloader

loader = ConfigLoader()
api_config = loader.load_api_config()

enabled_api = next(api for api in api_config.apis if api.enabled)

downloader = Downloader(enabled_api)

records = downloader.download()

print()

print(f"API : {enabled_api.name}")

print(f"Downloaded : {len(records)} records")

print()

print(records[0])

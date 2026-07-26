from enterprise_platform.ingestion.config_loader import ConfigLoader
from enterprise_platform.ingestion.ingestion_service import IngestionService


def main() -> None:
    print("Loading configuration...")

    loader = ConfigLoader()

    environment = loader.load_environment()
    api = loader.get_enabled_apis()[0]

    print(f"Running ingestion for API: {api.name}")

    service = IngestionService(
        api_config=api,
        environment=environment,
    )

    result = service.run()

    print("\nIngestion completed successfully!\n")

    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()

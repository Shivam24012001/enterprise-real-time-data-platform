from enterprise_platform.ingestion.config_loader import ConfigLoader

loader = ConfigLoader()

api_config = loader.load_api_config()
env_config = loader.load_environment()

print()

print("Environment")

print("------------------")

print(env_config.environment)


print()


print("Enables APIS")

for api in api_config.apis:
    if api.enabled:
        print(api.name)

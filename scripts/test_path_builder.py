from enterprise_platform.storage.path_builder import PathBuilder


def main():
    builder = PathBuilder()

    object_key = builder.build_object_key(
        api_name="jsonplaceholder",
        endpoint="posts",
    )

    print("\nGenerated Object Key:")
    print(object_key)


if __name__ == "__main__":
    main()

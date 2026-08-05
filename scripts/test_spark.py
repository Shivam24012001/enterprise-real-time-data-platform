from enterprise_platform.processing.spark_session import SparkSessionFactory


def main() -> None:
    spark = SparkSessionFactory.create()

    print("Spark Version", spark.version)
    print("Spark Session Created Successfully!")

    spark.stop()


if __name__ == "__main__":
    main()

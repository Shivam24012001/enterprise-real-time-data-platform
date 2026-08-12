from enterprise_platform.processing.reader import DataFrameReader
from enterprise_platform.processing.schemas import POST_SCHEMA
from enterprise_platform.processing.spark_session import SparkSessionFactory


def main() -> None:

    spark = SparkSessionFactory.create()

    reader = DataFrameReader(spark)

    print("\n========== USING EXPLICIT SCHEMA ==========\n")

    df = reader.read_json(
        "data/raw/sample/posts_invalid.json",
        schema=POST_SCHEMA,
    )

    df.printSchema()

    df.show(5, truncate=False)

    print("\nRecord Count:", df.count())

    spark.stop()


if __name__ == "__main__":
    main()

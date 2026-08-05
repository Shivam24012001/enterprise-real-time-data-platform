from enterprise_platform.processing.reader import DataFrameReader
from enterprise_platform.processing.spark_session import SparkSessionFactory


def main() -> None:

    spark = SparkSessionFactory.create()

    reader = DataFrameReader(spark)

    df = reader.read_json("data/raw/sample/posts_20260726_162513.json")

    print("\nSchema\n")

    df.printSchema()

    print("\nSample Data\n")

    df.show(5, truncate=False)

    print("\nRecord Count")

    print(df.count())

    spark.stop()


if __name__ == "__main__":
    main()

from enterprise_platform.processing.quality.validator import (
    DataQualityValidator,
)
from enterprise_platform.processing.reader import DataFrameReader
from enterprise_platform.processing.schemas import POST_SCHEMA
from enterprise_platform.processing.spark_session import SparkSessionFactory


def main() -> None:

    spark = SparkSessionFactory.create()

    reader = DataFrameReader(spark)

    dataframe = reader.read_json(
        "data/raw/sample/posts_20260726_162513.json",
        schema=POST_SCHEMA,
    )

    validator = DataQualityValidator(dataframe)

    required_columns = [
        "id",
        "userId",
        "title",
        "body",
    ]

    key_columns = [
        "id",
    ]

    report = validator.generate_report(
        required_columns=required_columns,
        key_columns=key_columns,
    )

    print("\nData Quality Report")
    print("===================")

    print(f"Total Records     : {report.total_records}")
    print(f"Missing Columns   : {report.missing_columns}")
    print(f"Null Counts       : {report.null_counts}")
    print(f"Duplicate Records : {report.duplicate_count}")
    print(f"Overall Status    : {report.status}")

    spark.stop()


if __name__ == "__main__":
    main()

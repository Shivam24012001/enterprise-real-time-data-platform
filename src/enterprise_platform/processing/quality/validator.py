from pyspark.sql import DataFrame

from enterprise_platform.processing.quality.quality_report import (
    QualityReport,
)


class DataQualityValidator:
    """performs reusable data quality validation on spark dataframe"""

    def __init__(self, dataframe: DataFrame) -> None:
        self.dataframe = dataframe

    def validate_required_columns(self, required_column: list[str]) -> list[str]:

        actual_columns = set(self.dataframe.columns)

        return [column for column in required_column if column not in actual_columns]

    def validate_nulls(self, columns: list[str]) -> dict[str, int]:
        """Return the number of NULL values for each specified columns"""

        null_counts: dict[str, int] = {}

        for column in columns:
            null_count = self.dataframe.filter(self.dataframe[column].isNull()).count()

            null_counts[column] = null_count

        return null_counts

    def validate_duplicates(self, key_columns: list[str]) -> int:
        """Return the number of duplicate records based on key columns"""

        total_counts = self.dataframe.count()

        unique_count = self.dataframe.select(*key_columns).distinct().count()

        return total_counts - unique_count

    def generate_report(
        self, required_columns: list[str], key_columns: list[str]
    ) -> QualityReport:
        """Run all data quality and generate the data quality report"""

        missing_columns = self.validate_required_columns(required_columns)

        null_counts = self.validate_nulls(required_columns)

        duplicate_count = self.validate_duplicates(key_columns)

        total_records = self.dataframe.count()

        has_nulls = any(count > 0 for count in null_counts.values())

        if missing_columns or has_nulls or duplicate_count > 0:
            status = "FAIL"
        else:
            status = "PASS"

        return QualityReport(
            total_records=total_records,
            missing_columns=missing_columns,
            null_counts=null_counts,
            duplicate_count=duplicate_count,
            status=status,
        )

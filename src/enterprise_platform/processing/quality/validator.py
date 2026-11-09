from pyspark.sql import DataFrame
import pytest

from enterprise_platform.processing.quality.quality_report import (
    QualityReport,
)


class DataQualityValidator:
    """Reusable data quality checks for spark DataFrame.
    Column match is exact and case sensitive: bronze keep source name."""

    def __init__(self, dataframe: DataFrame) -> None:
        self.dataframe = dataframe
        self._available = set(dataframe.columns)

    def split_columns(self, columns: list[str]) -> tuple[list[str], list[str]]:
        """Return (present, missing), keeping input order and dropping repeats."""
        seen: set[str] = set()
        present: list[str] = []
        missing: list[str] = []
        for column in columns:
            if column in seen:
                continue
            else:
                seen.add(column)
            if column in self._available:
                present.append(column)
            else:
                missing.append(column)

        return present, missing

    def validate_required_columns(self, required_column: list[str]) -> list[str]:

        _, missing = self.split_columns(required_column)
        return missing

    def validate_nulls(self, columns: list[str]) -> dict[str, int]:
        """Return the number of NULL values for each specified columns"""

        null_counts: dict[str, int] = {}
        present, _ = self.split_columns(columns)

        for column in present:
            null_count = self.dataframe.filter(self.dataframe[column].isNull()).count()

            null_counts[column] = null_count

        return null_counts

    def validate_duplicates(self, key_columns: list[str]) -> int:
        """Return the number of duplicate records based on key columns"""
        present, missing = self.split_columns(key_columns)

        if missing:
            return None

        total_counts = self.dataframe.count()

        unique_count = self.dataframe.select(*present).distinct().count()

        return total_counts - unique_count

    def generate_report(
        self, required_columns: list[str], key_columns: list[str]
    ) -> QualityReport:
        """Run all data quality and generate the data quality report"""

        missing_columns = self.validate_required_columns(required_columns + key_columns)

        null_counts = self.validate_nulls(required_columns)

        duplicate_count = self.validate_duplicates(key_columns)

        total_records = self.dataframe.count()

        has_nulls = any(count > 0 for count in null_counts.values())
        duplicates_failed = duplicate_count is None or duplicate_count > 0

        if missing_columns or has_nulls or duplicates_failed:
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

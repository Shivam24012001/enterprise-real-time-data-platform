from typing import Literal

from pydantic import BaseModel

from enterprise_platform.processing.quality.exceptions import DataQualityError


class QualityReport(BaseModel):
    """Results of data quality checks for one DataFrame."""

    total_records: int
    missing_columns: list[str]
    null_counts: dict[str, int]
    duplicate_count: int | None
    status: Literal["PASS", "FAIL"]

    def failure_messages(self) -> list[str]:
        """Human-readable reason for every failed check, in a fixed order."""
        messages: list[str] = []

        if self.missing_columns:
            messages.append(f"missing columns: {self.missing_columns}")

        for column, count in self.null_counts.items():
            if count > 0:
                messages.append(f"column '{column}' has {count} null value(s)")

        if self.duplicate_count is None:
            messages.append("duplicate check skipped: key column missing")
        elif self.duplicate_count > 0:
            messages.append(f"{self.duplicate_count} duplicate row(s) by key")

        return messages

    def raise_if_failed(self) -> None:
        """Raise DataQualityError when status is FAIL; do nothing on PASS."""
        if self.status == "PASS":
            return

        reasons = "; ".join(self.failure_messages())
        raise DataQualityError(f"Data quality check failed: {reasons}", report=self)

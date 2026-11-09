from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from enterprise_platform.processing.quality.quality_report import QualityReport


class DataQualityError(Exception):
    """Raised when a DataFrame fails its data quality checks."""

    def __init__(self, message: str, report: QualityReport) -> None:
        super().__init__(message)
        self.report = report  # caller can inspect the full report

from pydantic import BaseModel
from typing import Literal


class QualityReport(BaseModel):
    """Results of data quality checks for one DataFrame."""

    total_records: int
    missing_columns: list[str]
    null_counts: dict[str, int]
    duplicate_count: int|None
    status: Literal["PASS", "FAIL"]

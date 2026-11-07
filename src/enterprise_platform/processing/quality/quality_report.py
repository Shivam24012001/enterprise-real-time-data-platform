from pydantic import BaseModel


class QualityReport(BaseModel):
    """Represent the results of data quality validations."""

    total_records: int
    missing_columns: list[str]
    null_counts: dict[str, int]
    duplicate_count: int
    status: str

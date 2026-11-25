from dataclasses import dataclass

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enterprise_platform.processing.reader import CORRUPT_COLUMN, SOURCE_FILE_COLUMN


@dataclass(frozen=True)
class QuarantineResult:
    """Rows that are safe to load, and how many were set aside."""

    good: DataFrame
    quarantined_count: int


def quarantine_corrupt_records(
    dataframe: DataFrame, quarantine_path: str
) -> QuarantineResult:
    """Write malformed records to quarantine_path and return the good rows.

    Expects a DataFrame read in PERMISSIVE mode. Each quarantined record keeps
    its raw text, the file it came from, a reason and the time it was set aside,
    so it can be inspected and replayed later. Good rows continue without the
    `_corrupt_record` column.
    """
    if CORRUPT_COLUMN not in dataframe.columns:
        return QuarantineResult(good=dataframe, quarantined_count=0)

    # Spark refuses queries that filter on the corrupt-record column of a raw
    # read; caching the parsed rows first is the documented workaround.
    cached = dataframe.cache()
    is_corrupt = F.col(CORRUPT_COLUMN).isNotNull()

    bad = cached.filter(is_corrupt)
    quarantined_count = bad.count()

    if quarantined_count:
        source_file = (
            F.col(SOURCE_FILE_COLUMN)
            if SOURCE_FILE_COLUMN in dataframe.columns
            else F.lit(None).cast("string")
        )
        (
            bad.select(
                F.col(CORRUPT_COLUMN).alias("raw_record"),
                source_file.alias("source_file"),
                F.lit("malformed_record").alias("reason"),
                F.current_timestamp().alias("quarantined_at"),
            )
            .write.mode("append")
            .json(quarantine_path)
        )

    good = cached.filter(~is_corrupt).drop(CORRUPT_COLUMN)
    return QuarantineResult(good=good, quarantined_count=quarantined_count)

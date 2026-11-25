from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, StructField, StructType

CORRUPT_COLUMN = "_corrupt_record"
SOURCE_FILE_COLUMN = "_source_file"
VALID_MODES = ("PERMISSIVE", "DROPMALFORMED", "FAILFAST")


class DataFrameReader:
    """Read raw files into Spark DataFrames."""

    def __init__(self, spark: SparkSession) -> None:
        self.spark = spark

    def read_json(
        self,
        file_path: str,
        schema: StructType | None = None,
        mode: str = "PERMISSIVE",
        multiline: bool = False,
    ) -> DataFrame:
        """Read JSON into a DataFrame and tag each row with the file it came from.

        Modes:
            PERMISSIVE    keep every row; a malformed record keeps its raw text in
                          `_corrupt_record` so it can be quarantined.
            DROPMALFORMED silently drop malformed records.
            FAILFAST      fail the read on the first malformed record.

        Use JSON Lines (one record per line, multiline=False) for per-record
        quarantine. A multi-line JSON array is parsed as a single record, so one
        bad record marks the whole file as corrupt.

        A missing field is not malformed: it becomes null and must be caught by
        the data quality checks (DataQualityValidator).
        """
        mode = mode.upper()
        if mode not in VALID_MODES:
            raise ValueError(f"mode must be one of {VALID_MODES}, got {mode!r}")

        reader = (
            self.spark.read.option("mode", mode)
            .option("multiLine", multiline)
            .option("columnNameOfCorruptRecord", CORRUPT_COLUMN)
        )

        if schema is not None:
            if mode == "PERMISSIVE" and CORRUPT_COLUMN not in schema.fieldNames():
                schema = StructType(
                    schema.fields + [StructField(CORRUPT_COLUMN, StringType())]
                )
            reader = reader.schema(schema)

        return reader.json(file_path).withColumn(
            SOURCE_FILE_COLUMN, F.col("_metadata.file_path")
        )

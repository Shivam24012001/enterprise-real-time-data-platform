from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType


class DataFrameReader:
    """read data into spark DataFrame"""

    def __init__(self, spark: SparkSession) -> None:
        self.spark = spark

    def read_json(
        self,
        file_path: str,
        schema: StructType | None = None,
        mode: str = "FAILFAST",
    ) -> DataFrame:
        """Read Json file into Spark Dataframe"""

        reader = self.spark.read.option("multiline", True)

        if schema is not None:
            reader = reader.schema(schema)

        return reader.json(file_path)

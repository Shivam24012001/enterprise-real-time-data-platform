from pyspark.sql import DataFrame, SparkSession


class DataFrameReader:
    """read data into spark DataFrame"""

    def __init__(self, spark: SparkSession) -> None:
        self.spark = spark

    def read_json(self, file_path: str) -> DataFrame:
        """Read Json file into Spark Dataframe"""

        return self.spark.read.option("Multiline", True).json(file_path)

from pyspark.sql import SparkSession


class SparkSessionFactory:
    """factory for creating and configuring spark session instance"""

    @staticmethod
    def create(app_name: str = "Enterprise Data Platform") -> SparkSession:
        return SparkSession.builder.appName(app_name).master("local[*]").getOrCreate()

    ## local → Run Spark on your own machine
    ## * → Use all available CPU cores.

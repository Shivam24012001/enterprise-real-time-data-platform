from pyspark.sql.types import LongType, StringType, StructField, StructType

POST_SCHEMA = StructType(
    [
        StructField("user_id", LongType(), nullable=False),
        StructField("id", LongType(), nullable=False),
        StructField("title", StringType(), nullable=False),
        StructField("body", StringType(), nullable=False),
    ]
)

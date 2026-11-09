import pytest

from enterprise_platform.processing.quality.exceptions import DataQualityError
from enterprise_platform.processing.quality.validator import DataQualityValidator


def test_raises_with_column_name_and_count(spark):
    df = spark.createDataFrame([(1, None), (2, None)], "id long, userId long")
    report = DataQualityValidator(df).generate_report(["id", "userId"], ["id"])

    with pytest.raises(
        DataQualityError, match=r"column 'userId' has 2 null value\(s\)"
    ):
        report.raise_if_failed()


def test_clean_data_passes(spark):
    df = spark.createDataFrame([(1, 10), (2, 20)], "id long , userId long")
    report = DataQualityValidator(df).generate_report(["id", "userId"], ["id"])
    assert report.status == "PASS"
    assert report.duplicate_count == 0
    assert report.missing_columns == []
    report.raise_if_failed()


def test_missing_column_reported_without_crash(spark):
    df = spark.createDataFrame([(1, 20), (3, 30)], "id long ,userId long")
    report = DataQualityValidator(df).generate_report(["id", "userId", "body"], ["id"])

    assert report.status == "FAIL"
    assert report.missing_columns == ["body"]
    assert "body" not in report.null_counts


def test_missing_key_column_skips_duplicates(spark):
    df = spark.createDataFrame([(1, 20), (3, 50)], "id long , userId long")
    report = DataQualityValidator(df).generate_report(
        required_columns=["id", "userId"], key_columns=["id", "body"]
    )

    assert report.status == "FAIL"
    assert report.duplicate_count is None


def test_column_match_is_case_sensitive(spark):
    df = spark.createDataFrame([(1, 20), (3, 40)], "id long, userId long")
    report = DataQualityValidator(df).generate_report(
        required_columns=["id", "userid"], key_columns=["id"]
    )

    assert "userid" in report.missing_columns

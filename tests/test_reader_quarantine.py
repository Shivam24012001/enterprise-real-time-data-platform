import pytest

from enterprise_platform.processing.quarantine import quarantine_corrupt_records
from enterprise_platform.processing.reader import CORRUPT_COLUMN, DataFrameReader
from enterprise_platform.processing.schemas import POST_SCHEMA

GOOD = '{"userId": 1, "id": %d, "title": "t", "body": "b"}'
BROKEN = '{"userId": 1, "id": 99, "title": "broken"'  # closing brace missing


def write_jsonl(path, lines):
    path.write_text("\n".join(lines) + "\n")
    return str(path)


def test_one_bad_row_is_quarantined_and_the_rest_continue(spark, tmp_path):
    schema=POST_SCHEMA,
    multiline=True,
    lines = [GOOD % i for i in range(1, 5)] + [BROKEN]
    source = write_jsonl(tmp_path / "posts.jsonl", lines)
    quarantine_dir = tmp_path / "quarantine"

    df = DataFrameReader(spark).read_json(source, schema=POST_SCHEMA)
    result = quarantine_corrupt_records(df, str(quarantine_dir))

    assert result.good.count() == 4
    assert result.quarantined_count == 1
    assert CORRUPT_COLUMN not in result.good.columns

    quarantined = spark.read.json(str(quarantine_dir)).collect()
    assert len(quarantined) == 1
    assert quarantined[0]["raw_record"] == BROKEN
    assert quarantined[0]["source_file"].endswith("posts.jsonl")
    assert quarantined[0]["reason"] == "malformed_record"


def test_clean_file_quarantines_nothing(spark, tmp_path):
    source = write_jsonl(tmp_path / "posts.jsonl", [GOOD % i for i in range(1, 4)])
    quarantine_dir = tmp_path / "quarantine"

    df = DataFrameReader(spark).read_json(source, schema=POST_SCHEMA)
    result = quarantine_corrupt_records(df, str(quarantine_dir))

    assert result.good.count() == 3
    assert result.quarantined_count == 0
    assert not quarantine_dir.exists()


def test_failfast_mode_is_applied(spark, tmp_path):
    source = write_jsonl(tmp_path / "posts.jsonl", [GOOD % 1, BROKEN])

    df = DataFrameReader(spark).read_json(source, schema=POST_SCHEMA, mode="FAILFAST")

    with pytest.raises(Exception, match="MALFORMED_RECORD"):
        df.collect()


def test_missing_field_is_not_malformed(spark, tmp_path):
    no_body = '{"userId": 1, "id": 1, "title": "t"}'
    source = write_jsonl(tmp_path / "posts.jsonl", [no_body])

    df = DataFrameReader(spark).read_json(source, schema=POST_SCHEMA)
    result = quarantine_corrupt_records(df, str(tmp_path / "quarantine"))

    assert result.quarantined_count == 0
    assert result.good.collect()[0]["body"] is None  # DataQualityValidator catches this


def test_multiline_array_marks_whole_file_corrupt(spark, tmp_path):
    path = tmp_path / "posts.json"
    path.write_text("[\n  " + GOOD % 1 + ",\n  " + BROKEN + "\n]")

    df = DataFrameReader(spark).read_json(str(path), schema=POST_SCHEMA, multiline=True)
    result = quarantine_corrupt_records(df, str(tmp_path / "quarantine"))

    assert result.good.count() == 0
    assert result.quarantined_count == 1


def test_unknown_mode_is_rejected(spark):
    with pytest.raises(ValueError, match="mode must be one of"):
        DataFrameReader(spark).read_json("unused.json", mode="STRICT")

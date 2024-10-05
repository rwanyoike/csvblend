import io
import sqlite3
from pathlib import Path

import pytest

from csvblend import MergeFiles, models
from csvblend.utils import hash_function

test_columns = ["first_name", "last_name", "score"]
test_indexes = test_columns[:2]
test_values = [
    ("Yú", "花", "£3.87"),
    ("Marlène", "贡", "€4.27"),
    ("Hélène", "於", "¥9.50"),
    ("Lorène", "阙", "¥4.55"),
    ("Gaëlle", "俞", "¥7.17"),
    ("Sòng", "禄", "$6.17"),
    ("Yáo", "暴", "$3.78"),
    ("Nuó", "辛", "$0.73"),
    ("Faîtes", "闵", "€0.06"),
    ("Yáo", "贺", "£5.18"),
]


def test_mergefile___init__():
    mf = MergeFiles(test_columns, test_indexes)
    assert mf.affected_count == 0
    assert mf.rowcount == 0
    assert mf.closed is False
    assert mf._columns == {hash_function(i): i for i in test_columns}
    assert mf._indexes == {hash_function(i): i for i in test_indexes}
    assert mf._db is None
    assert mf._connection is None
    assert mf._table == "merge_table"
    assert mf._merge_count == 0


def test_mergefile___init___with_database(tmp_path: Path):
    test_database = tmp_path / "test.db"
    mf = MergeFiles(test_columns, test_indexes, str(test_database))
    assert mf._db == str(test_database)


def test_mergefile___init___sqlite_version(mocker):
    mocker.patch.object(models.sqlite3, "sqlite_version_info", (3, 23, 1))
    mocker.patch.object(models.sqlite3, "sqlite_version", "3.23.1")
    with pytest.raises(
        Exception,
        match=r"SQLite 3.24.0 \(2018-06-04\) or later is required \(found 3.23.1\)",
    ):
        MergeFiles(test_columns, test_indexes)


def test_mergefile___init___exception():
    with pytest.raises(ValueError, match="columns should be a list or tuple"):
        MergeFiles("invalid", test_indexes)
    with pytest.raises(ValueError, match="indexes should be a list or tuple"):
        MergeFiles(test_columns, "invalid")
    with pytest.raises(ValueError, match="indexes is an empty sequence"):
        MergeFiles(test_columns, [])
    with pytest.raises(ValueError, match="columns is an empty sequence"):
        MergeFiles([], [])
    with pytest.raises(ValueError, match="indexes must be a subset of columns"):
        MergeFiles(test_columns, ["unknown"])
    with pytest.raises(ValueError, match="columns contains duplicate items"):
        MergeFiles(test_columns + test_columns, test_indexes)
    with pytest.raises(ValueError, match="indexes contains duplicate items"):
        MergeFiles(test_columns, test_indexes + test_indexes)


def test_mergefile_merge():
    test_headers = ",".join(test_columns)
    csvfiles = [
        f"{test_headers}\nMaéna,柴,$0.47\nMaïwenn,车,¥0.56\n",
        f"{test_headers}\nMaéna,柴,¥5.47\nGöran,酆,$1.39\n",
        f"{test_headers}\nAurélie,沙,€9.30\n",
        f"{test_headers}\nMaéna,柴,$0.47\nMaïwenn,车,¥9.00\n",
        f"{test_headers}\nBérénice,屈,¥6.01\nAurélie,沙,€9.30\n",
    ]
    mf = MergeFiles(test_columns, test_indexes)
    for csvfile in csvfiles:
        mf.merge(io.StringIO(csvfile))
    assert mf.affected_count == 6
    assert mf.rowcount == 5
    assert mf._merge_count == 5
    test_cursor0 = mf._connection.execute(f"""
        SELECT * from {mf._table};
    """).fetchall()
    assert test_cursor0 == [
        ("Maéna", "柴", "$0.47"),
        ("Maïwenn", "车", "¥9.00"),
        ("Göran", "酆", "$1.39"),
        ("Aurélie", "沙", "€9.30"),
        ("Bérénice", "屈", "¥6.01"),
    ]


def test_mergefile_merge_noncontiguous_index():
    columns = ["first_name", " ", "score", "email", " ip addr "]
    indexes = [" ", "email"]
    test_headers = ",".join(columns)
    csvfiles = [
        f"{test_headers}\n"
        f"Maïlis,和,¥3.11,jvenn0@bloglovin.com,249.156.88.77\n"
        f"Danièle,胡,€7.20,bgorringe1@disqus.com,174.198.123.229\n",
        f"{test_headers}\n" f"Rachèle,郜,¥9.01,wmerriday2@patch.com,39.135.210.166\n",
        f"{test_headers}\n"
        f"Maïlis,和,¥5.46,jvenn0@bloglovin.com,60.23.102.202\n"
        f"Rachèle,郜,¥9.01,wmerriday2@patch.com,39.135.210.166\n",
        f"{test_headers}\n"
        f"Faîtes,胡,£2.61,bgorringe1@disqus.com,185.204.124.234\n"
        f"Stévina,隆,€9.82,zpiwell6@theguardian.com,114.205.62.133\n",
        f"{test_headers}\n" f"Lyséa,胡,$3.05,bgorringe1@disqus.com,29.168.3.116\n",
        f"{test_headers}\n"
        f"Torbjörn,那,¥7.93,cbarke8@ihg.com,232.157.135.140\n"
        f"Lyséa,胡,$3.05,bgorringe1@disqus.com,29.168.3.116\n",
    ]
    mf = MergeFiles(columns, indexes)
    for csvfile in csvfiles:
        mf.merge(io.StringIO(csvfile))
    assert mf.affected_count == 6
    assert mf.rowcount == 5
    assert mf._merge_count == 6
    test_cursor0 = mf._connection.execute(f"""
        SELECT * from {mf._table};
    """).fetchall()
    assert test_cursor0 == [
        ("Maïlis", "和", "¥5.46", "jvenn0@bloglovin.com", "60.23.102.202"),
        ("Lyséa", "胡", "$3.05", "bgorringe1@disqus.com", "29.168.3.116"),
        ("Rachèle", "郜", "¥9.01", "wmerriday2@patch.com", "39.135.210.166"),
        ("Stévina", "隆", "€9.82", "zpiwell6@theguardian.com", "114.205.62.133"),
        ("Torbjörn", "那", "¥7.93", "cbarke8@ihg.com", "232.157.135.140"),
    ]


def test_mergefile_merge_exception():
    test_headers = ",".join(test_columns)
    csvfiles = [
        f"{test_headers}\nMaéna,柴,$0.47\nMaïwenn,车,¥0.56\n",
        f"{test_headers}\nMaéna,柴,¥5.47\nGöran,酆,$1.39\n",
        f"{test_headers}\nAurélie,沙,€9.30\n",
        f"{test_headers}\nMaéna,柴,$0.47\nMaïwenn,车,¥9.00\n",
        f"{test_headers}\nBérénice,屈,¥6.01\nAurélie,沙,€9.30\n",
    ]
    mf = MergeFiles(test_columns + ["unknown"], test_indexes)
    for csvfile in csvfiles:
        with pytest.raises(
            ValueError, match=r"fieldnames .+ must be a subset of columns"
        ):
            mf.merge(io.StringIO(csvfile))


def test_mergefile_rows():
    test_headers = ",".join(test_columns)
    csvfiles = [
        f"{test_headers}\nMaéna,柴,$0.47\nMaïwenn,车,¥0.56\n",
        f"{test_headers}\nMaéna,柴,¥5.47\nGöran,酆,$1.39\n",
    ]
    mf = MergeFiles(test_columns, test_indexes)
    assert list(mf.rows()) == []
    for csvfile in csvfiles:
        mf.merge(io.StringIO(csvfile))
    assert list(mf.rows()) == [
        ("Maéna", "柴", "¥5.47"),
        ("Maïwenn", "车", "¥0.56"),
        ("Göran", "酆", "$1.39"),
    ]


def test_mergefile_cleanup():
    mf = MergeFiles(test_columns, test_indexes)
    mf.merge(io.StringIO(",".join(test_columns)))
    assert Path(mf._db).exists()
    mf.cleanup()
    assert not Path(mf._db).exists()
    assert mf.closed is True
    with pytest.raises(sqlite3.ProgrammingError) as excinfo:
        mf._connection.execute("""
            SELECT name FROM sqlite_master
            LIMIT 1;
        """)
    assert "closed database" in str(excinfo.value)
    mf.cleanup()


def test_mergefile_cleanup_context_manager():
    with MergeFiles(test_columns, test_indexes, ":memory:") as mf:
        mf.merge(io.StringIO(",".join(test_columns)))
    assert mf.closed is True


def test_mergefile_cleanup_exception():
    test_message = "Operation on closed MergeFile"
    mf = MergeFiles(test_columns, test_indexes)
    mf.cleanup()
    assert mf.closed is True
    with pytest.raises(ValueError, match=test_message):
        mf.merge(io.StringIO(",".join(test_columns)))
    with pytest.raises(ValueError, match=test_message):
        next(mf.rows())

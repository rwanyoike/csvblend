import re
import sqlite3
from pathlib import Path

from csvblend import csvblend

test_table = "test_table"
test_columns = ["first_name", "last_name", "score"]
test_indexes = test_columns[:2]
test_values = [
    ("Yú", "花", "£3.87"),
    ("Marlène", "贡", "€4.27"),
    ("Hélène", "於", "¥9.50"),
    ("Hélène", "於", "¥9.50"),
    ("Gaëlle", "俞", "¥7.17"),
    ("Sòng", "禄", "$6.17"),
    ("Hélène", "於", "¥9.50"),
    ("Nuó", "辛", "$0.73"),
    ("Faîtes", "闵", "€0.06"),
    ("Yáo", "贺", "£5.18"),
]


def test_create_database(tmp_path: Path):
    test_database = tmp_path / "test.db"
    assert not test_database.exists()
    connection = csvblend.create_database(str(test_database))
    assert test_database.exists()
    assert isinstance(connection, sqlite3.Connection)
    test_cursor0 = connection.execute("""
        PRAGMA database_list;
    """).fetchall()
    assert test_cursor0 == [(0, "main", str(test_database))]
    test_cursor1 = connection.execute("""
        PRAGMA journal_mode;
    """).fetchone()
    assert test_cursor1[0] == "off"
    test_cursor2 = connection.execute("""
        PRAGMA synchronous;
    """).fetchone()
    assert test_cursor2[0] == 0


def test_create_database_in_memory():
    connection = csvblend.create_database(":memory:")
    test_cursor0 = connection.execute("""
        PRAGMA database_list;
    """).fetchall()
    assert test_cursor0 == [(0, "main", "")]


def test_create_table(tmp_path: Path):
    def _normalize_text(text):
        return " ".join(re.findall(r"\S+", text))

    test_database = tmp_path / "test.db"
    connection = sqlite3.connect(str(test_database))
    cursor = csvblend.create_table(connection, test_table, test_columns, test_indexes)
    assert isinstance(cursor, sqlite3.Cursor)
    test_cursor0 = connection.execute("""
        SELECT name, sql FROM sqlite_master
        WHERE type='table';
    """).fetchone()
    assert test_cursor0[0] == test_table
    assert _normalize_text(test_cursor0[1]) == _normalize_text(f"""
        CREATE TABLE {test_table} ("first_name" TEXT, "last_name" TEXT, "score" TEXT,
        UNIQUE ("first_name", "last_name"))
    """)


def test_insert_values(tmp_path: Path):
    test_database = tmp_path / "test.db"
    connection = sqlite3.connect(str(test_database))
    connection.execute(f"""
        CREATE TABLE {test_table} ("first_name" TEXT, "last_name" TEXT, "score" TEXT,
        UNIQUE ("first_name", "last_name"));
    """)
    cursor = csvblend.insert_values(
        connection, test_table, test_columns, test_indexes, test_values
    )
    assert isinstance(cursor, sqlite3.Cursor)
    assert cursor.rowcount == 8
    test_cursor0 = connection.execute(f"""
        SELECT * from {test_table};
    """).fetchall()
    assert test_cursor0 == list(dict.fromkeys(test_values))


def test_insert_values_all_indexes(tmp_path: Path):
    test_database = tmp_path / "test.db"
    connection = sqlite3.connect(str(test_database))
    connection.execute(f"""
        CREATE TABLE {test_table} ("first_name" TEXT, "last_name" TEXT, "score" TEXT,
        UNIQUE ("first_name", "last_name", "score"));
    """)
    csvblend.insert_values(
        connection, test_table, test_columns, test_columns, test_values
    )
    test_cursor0 = connection.execute(f"""
        SELECT * from {test_table};
    """).fetchall()
    assert test_cursor0 == list(dict.fromkeys(test_values))


def test_select_values(tmp_path: Path):
    test_database = tmp_path / "test.db"
    connection = sqlite3.connect(str(test_database))
    connection.execute(f"""
        CREATE TABLE {test_table} ("first_name" TEXT, "last_name" TEXT, "score" TEXT);
    """)
    connection.executemany(f"""
        INSERT INTO {test_table} ("first_name", "last_name", "score")
        VALUES (?, ?, ?);
    """, test_values)
    cursor = csvblend.select_values(connection, test_table, test_columns)
    assert isinstance(cursor, sqlite3.Cursor)
    assert cursor.fetchall() == test_values


def test_select_count(tmp_path: Path):
    test_database = tmp_path / "test.db"
    connection = sqlite3.connect(str(test_database))
    connection.execute(f"""
        CREATE TABLE {test_table} ("first_name" TEXT, "last_name" TEXT, "score" TEXT);
    """)
    connection.executemany(f"""
        INSERT INTO {test_table} ("first_name", "last_name", "score")
        VALUES (?, ?, ?);
    """, test_values)
    cursor = csvblend.select_count(connection, test_table)
    assert isinstance(cursor, sqlite3.Cursor)
    assert cursor.fetchall() == [(10,)]

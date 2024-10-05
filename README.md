# csvblend: Python CSV Merge Library

[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/rwanyoike/csvblend-python-library/python-package.yml?branch=main)
](https://github.com/rwanyoike/csvblend-python-library/actions/workflows/python-package.yml?query=branch%3Amain)
[![GitHub License](https://img.shields.io/github/license/rwanyoike/csvblend-python-library)
](LICENSE.txt)
[![PyPI - Version](https://img.shields.io/pypi/v/csvblend)
](https://pypi.org/project/csvblend)

> Join or merge multiple CSVs.

csvblend is a Python library to merge multiple CSVs based on a list of columns efficiently.

NOTE: csvblend requires SQLite version 3.24.0 (2018-06-04) or better:

```shell
python -c 'import sqlite3; print(sqlite3.sqlite_version)'
```

Basic merge usage:

```python
>>> from csvblend import MergeFiles
>>> columns = ["field1", "field2", "field3"]
>>> indexes = ["field1"]
>>> with MergeFiles(columns, indexes) as mf:
...     with open("csvfile1") as fp:
...         mf.merge(fp)
...     with open("csvfile2") as fp:
...         mf.merge(fp)
...     with open("csvfile3") as fp:
...         mf.merge(fp)
...     for row in mf.rows():
...         print(row)
```

[Features](#features) | [Installation](#installation) | [Usage](#usage) | [Contributing](#contributing) | [License](#license)

## Features

- [SQLite](https://www.sqlite.org) (RDBMS) under the hood.
- Affected row count (created or updated) -- show changes between CSVs.
- No external dependencies.

csvblend officially supports Python 3.8+.

## Installation

To install csvblend, simply run:

```shell
$ pip install -U csvblend
✨🖇✨
```

## Usage

For documentation, see [`./docs/README.md`](./docs/README.md).

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the [MIT License](./LICENSE).

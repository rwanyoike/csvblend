# csvblend Documentation

## Table of Contents

- [Basic Module Usage](#basic-module-usage)
- [`with` statement](#with-statement)

## Basic Module Usage

Here is an interactive session showing some of the basic commands:

```
./mon-input.csv:                ./tue-input.csv:                ./wed-input.csv:

|planet |name    |measurement|  |planet |name    |measurement|  |planet |name    |measurement|
|-------|--------|-----------|  |-------|--------|-----------|  |-------|--------|-----------|
|jupiter|kale    |14         |  |saturn |titan   |64         |  |neptune|thalassa|-9         |
|saturn |titan   |3          |  |uranus |umbriel |76         |  |uranus |rosalind|54         |
|uranus |belinda |7          |  |jupiter|iocaste |-34        |  |jupiter|kale    |TBD        |
|neptune|thalassa|TBD        |  |mars   |phobos  |55         |
|uranus |rosalind|54         |
```

```python
>>> from csvblend import MergeFiles

# Create a MergeFiles instance
>>> columns = ["planet", "name", "measurement"]
>>> indexes = ["planet", "name"]
>>> mf = MergeFiles(columns, indexes)

# Merge mon-input.csv
>>> with open("mon-input.csv") as fp:
...     mf.merge(fp)
...

# mon-input.csv created 5 new rows
#               updated 0 current rows
>>> mf.rowcount, mf.affected_count
(5, 0)

# Merge tue-input.csv
>>> with open("tue-input.csv") as fp:
...     mf.merge(fp)
...

# tue-input.csv created 3 new rows
#               updated 1 current row
>>> mf.rowcount, mf.affected_count
(8, 4)

# Merge wed-input.csv
>>> with open("wed-input.csv") as fp:
...     mf.merge(fp)
...

# wed-input.csv created 0 new rows
#               updated 3 current rows
>>> mf.rowcount, mf.affected_count
(8, 6)

# Print out the merge CSV rows
>>> for row in mf.rows():
...     print(row)
...
('jupiter', 'kale', 'TBD')
('saturn', 'titan', '64')
('uranus', 'belinda', '7')
('neptune', 'thalassa', '-9')
('uranus', 'rosalind', '54')
('uranus', 'umbriel', '76')
('jupiter', 'iocaste', '-34')
('mars', 'phobos', '55')

# Close the MergeFiles instance
>>> mf.cleanup()
```

## `with` statement

csvblend's instances are _context managers_ and can be used with the `with` statement:

```python
>>> with MergeFiles(columns, indexes) as mf:
...     for csvfile in csvfiles:
...         with open(csvfile) as fp:
...             mf.merge(fp)
...     for row in mf.rows():
...         print(row)
```

When an instance exits the `with` block, the `.cleanup()` method is called.

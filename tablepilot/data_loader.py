"""
Data loader module - Multi-format data loading with intelligent detection.
Supports CSV, TSV, JSON, JSON Lines, and Excel-like formats.
Zero external dependencies - pure Python implementation.
"""

import csv
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple, Union


class DataTable:
    """Lightweight in-memory tabular data structure.

    Stores data as a list of dictionaries (row-oriented) and provides
    efficient column access, type inference, and basic operations.
    """

    def __init__(self, columns: List[str], rows: List[List[Any]], source: str = ""):
        self.columns = columns
        self._rows = rows
        self.source = source
        self._column_cache: Dict[str, List[Any]] = {}

    @property
    def rows(self) -> List[Dict[str, Any]]:
        """Return rows as list of dicts."""
        return [dict(zip(self.columns, row)) for row in self._rows]

    @property
    def shape(self) -> Tuple[int, int]:
        """Return (num_rows, num_columns)."""
        return (len(self._rows), len(self.columns))

    @property
    def num_rows(self) -> int:
        return len(self._rows)

    @property
    def num_columns(self) -> int:
        return len(self.columns)

    def column(self, name: str) -> List[Any]:
        """Get all values for a column."""
        if name in self._column_cache:
            return self._column_cache[name]
        if name not in self.columns:
            raise KeyError(f"Column '{name}' not found. Available: {self.columns}")
        idx = self.columns.index(name)
        values = [row[idx] for row in self._rows]
        self._column_cache[name] = values
        return values

    def set_column(self, name: str, values: List[Any]) -> None:
        """Set values for a column."""
        if name not in self.columns:
            raise KeyError(f"Column '{name}' not found")
        idx = self.columns.index(name)
        for i, val in enumerate(values):
            if i < len(self._rows):
                self._rows[i][idx] = val
        if name in self._column_cache:
            del self._column_cache[name]

    def head(self, n: int = 5) -> "DataTable":
        """Return first n rows."""
        return DataTable(self.columns[:], [row[:] for row in self._rows[:n]], self.source)

    def tail(self, n: int = 5) -> "DataTable":
        """Return last n rows."""
        return DataTable(self.columns[:], [row[:] for row in self._rows[-n:]], self.source)

    def sample(self, n: int = 10) -> "DataTable":
        """Return random sample of n rows."""
        import random
        indices = random.sample(range(len(self._rows)), min(n, len(self._rows)))
        return DataTable(self.columns[:], [self._rows[i][:] for i in sorted(indices)], self.source)

    def filter_rows(self, predicate) -> "DataTable":
        """Filter rows by predicate function."""
        filtered = [row for row in self._rows if predicate(dict(zip(self.columns, row)))]
        return DataTable(self.columns[:], [row[:] for row in filtered], self.source)

    def select_columns(self, names: List[str]) -> "DataTable":
        """Select specific columns."""
        indices = [self.columns.index(n) for n in names]
        new_cols = [self.columns[i] for i in indices]
        new_rows = [[row[i] for i in indices] for row in self._rows]
        return DataTable(new_cols, new_rows, self.source)

    def to_csv(self, path: str) -> None:
        """Export to CSV file."""
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.columns)
            writer.writerows(self._rows)

    def to_json(self, path: str) -> None:
        """Export to JSON file."""
        data = self.rows
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    def to_tsv(self, path: str) -> None:
        """Export to TSV file."""
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(self.columns)
            writer.writerows(self._rows)

    def __repr__(self) -> str:
        return f"DataTable(rows={self.num_rows}, columns={self.num_columns}, source='{self.source}')"

    def __len__(self) -> int:
        return self.num_rows


def detect_format(file_path: str) -> str:
    """Detect file format from extension and content.

    Returns: 'csv', 'tsv', 'json', 'jsonl', or 'unknown'
    """
    ext = os.path.splitext(file_path)[1].lower()

    format_map = {
        ".csv": "csv",
        ".tsv": "tsv",
        ".tab": "tsv",
        ".json": "json",
        ".jsonl": "jsonl",
        ".ndjson": "jsonl",
    }

    if ext in format_map:
        return format_map[ext]

    # Try content-based detection
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            if first_line.startswith(("[", "{")):
                return "json"
            if "\t" in first_line and "," not in first_line:
                return "tsv"
            return "csv"
    except Exception:
        return "unknown"


def detect_delimiter(file_path: str, format_hint: str = "") -> str:
    """Detect CSV delimiter by analyzing the first few lines."""
    if format_hint == "tsv":
        return "\t"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [f.readline() for _ in range(min(5, 100))]

        if not lines:
            return ","

        candidates = [",", "\t", ";", "|"]
        scores = {}

        for delim in candidates:
            counts = [line.count(delim) for line in lines if line.strip()]
            if not counts:
                continue
            scores[delim] = (
                sum(1 for c in counts if c > 0) / len(counts),  # consistency
                min(counts) if counts else 0,  # minimum count
            )

        best = max(scores, key=lambda d: (scores[d][0], scores[d][1]))
        return best if scores[best][0] > 0.5 else ","
    except Exception:
        return ","


def infer_value(value: str) -> Any:
    """Infer the Python type of a string value.

    Tries to parse as: int -> float -> bool -> None -> str
    """
    if value is None:
        return None

    if isinstance(value, (int, float, bool)):
        return value

    s = str(value).strip()

    if s == "":
        return None

    # None-like values
    if s.lower() in ("null", "none", "nil", "n/a", "na", "-", "nan", "NaN"):
        return None

    # Boolean
    if s.lower() in ("true", "yes", "1"):
        return True
    if s.lower() in ("false", "no", "0"):
        return False

    # Integer
    try:
        int_val = int(s)
        # Avoid converting "01" style strings
        if s == str(int_val) or (s.startswith("-") and s[1:] == str(abs(int_val))):
            return int_val
    except (ValueError, OverflowError):
        pass

    # Float
    try:
        return float(s)
    except (ValueError, OverflowError):
        pass

    return s


def infer_column_type(values: List[Any]) -> str:
    """Infer the type of a column from its values.

    Returns: 'integer', 'float', 'boolean', 'string', 'datetime', 'mixed'
    """
    non_none = [v for v in values if v is not None]
    if not non_none:
        return "empty"

    type_counts = {"integer": 0, "float": 0, "boolean": 0, "string": 0}

    for v in non_none:
        if isinstance(v, bool):
            type_counts["boolean"] += 1
        elif isinstance(v, int):
            type_counts["integer"] += 1
        elif isinstance(v, float):
            type_counts["float"] += 1
        else:
            s = str(v).strip()
            # Check for datetime patterns
            dt_patterns = [
                r"^\d{4}-\d{2}-\d{2}",  # ISO date
                r"^\d{2}/\d{2}/\d{4}",  # US date
                r"^\d{4}/\d{2}/\d{2}",  # Alternative
                r"^\d{2}-\d{2}-\d{4}",  # EU date
            ]
            for pat in dt_patterns:
                if re.match(pat, s):
                    return "datetime"
            type_counts["string"] += 1

    total = len(non_none)
    for t in ["integer", "boolean", "float"]:
        if type_counts[t] / total >= 0.8:
            return t

    if type_counts["float"] + type_counts["integer"] >= total * 0.8:
        return "float"

    return "string"


def load_csv(file_path: str, delimiter: str = ",", max_rows: int = 0,
             encoding: str = "utf-8") -> DataTable:
    """Load data from a CSV/TSV file."""
    rows = []
    columns = []

    encodings = [encoding, "utf-8-sig", "latin-1", "gbk", "gb2312"]

    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc, newline="") as f:
                reader = csv.reader(f, delimiter=delimiter)
                columns = next(reader, None)
                if not columns:
                    return DataTable([], [], file_path)

                # Clean column names
                columns = [c.strip().strip('"').strip("'") for c in columns]

                for i, row in enumerate(reader):
                    if max_rows > 0 and i >= max_rows:
                        break
                    if len(row) == 0 or all(c.strip() == "" for c in row):
                        continue
                    # Pad or trim row to match columns
                    while len(row) < len(columns):
                        row.append(None)
                    parsed = [infer_value(v.strip()) if v.strip() else None for v in row[:len(columns)]]
                    rows.append(parsed)

            return DataTable(columns, rows, file_path)
        except (UnicodeDecodeError, UnicodeError):
            continue

    raise ValueError(f"Cannot read file '{file_path}' with any supported encoding")


def load_json(file_path: str, max_rows: int = 0) -> DataTable:
    """Load data from a JSON file (array of objects or object with array)."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle different JSON structures
    if isinstance(data, list):
        if len(data) == 0:
            return DataTable([], [], file_path)
        if isinstance(data[0], dict):
            columns = list(data[0].keys())
            rows = [[item.get(c) for c in columns] for item in (data[:max_rows] if max_rows else data)]
        elif isinstance(data[0], list):
            columns = [f"col_{i}" for i in range(len(data[0]))]
            rows = data[:max_rows] if max_rows else data
        else:
            columns = ["value"]
            rows = [[v] for v in (data[:max_rows] if max_rows else data)]
    elif isinstance(data, dict):
        # Find the first array value
        for key, val in data.items():
            if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
                columns = list(val[0].keys())
                rows = [[item.get(c) for c in columns] for item in (val[:max_rows] if max_rows else val)]
                return DataTable(columns, rows, file_path)
        # Use dict keys as columns, values as single row
        columns = list(data.keys())
        rows = [[data[c] for c in columns]]
    else:
        raise ValueError(f"Unsupported JSON structure in '{file_path}'")

    return DataTable(columns, rows, file_path)


def load_jsonl(file_path: str, max_rows: int = 0) -> DataTable:
    """Load data from a JSON Lines file."""
    rows = []
    columns = []

    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if max_rows > 0 and i >= max_rows:
                break
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if isinstance(obj, dict):
                if not columns:
                    columns = list(obj.keys())
                rows.append([obj.get(c) for c in columns])

    return DataTable(columns, rows, file_path)


def load_file(file_path: str, max_rows: int = 0, columns: Optional[List[str]] = None) -> DataTable:
    """Load data from a file with automatic format detection.

    Args:
        file_path: Path to the data file
        max_rows: Maximum rows to load (0 = all)
        columns: Optional list of columns to select

    Returns:
        DataTable instance
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: '{file_path}'")

    fmt = detect_format(file_path)

    if fmt == "csv":
        delimiter = detect_delimiter(file_path)
        table = load_csv(file_path, delimiter=delimiter, max_rows=max_rows)
    elif fmt == "tsv":
        table = load_csv(file_path, delimiter="\t", max_rows=max_rows)
    elif fmt == "json":
        table = load_json(file_path, max_rows=max_rows)
    elif fmt == "jsonl":
        table = load_jsonl(file_path, max_rows=max_rows)
    else:
        # Default to CSV
        delimiter = detect_delimiter(file_path)
        table = load_csv(file_path, delimiter=delimiter, max_rows=max_rows)

    if columns:
        available = [c for c in columns if c in table.columns]
        if available:
            table = table.select_columns(available)

    return table

"""Unit tests for TablePilot data loader module."""

import json
import os
import sys
import tempfile
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tablepilot.data_loader import (
    DataTable, load_file, detect_format, infer_value, infer_column_type,
)


class TestDataTable(unittest.TestCase):
    """Test DataTable operations."""

    def setUp(self):
        self.table = DataTable(
            columns=["name", "age", "score"],
            rows=[
                ["Alice", 25, 85.5],
                ["Bob", 30, 92.0],
                ["Charlie", None, 78.0],
                ["Diana", 28, None],
            ],
        )

    def test_shape(self):
        self.assertEqual(self.table.shape, (4, 3))
        self.assertEqual(self.table.num_rows, 4)
        self.assertEqual(self.table.num_columns, 3)

    def test_column(self):
        names = self.table.column("name")
        self.assertEqual(names, ["Alice", "Bob", "Charlie", "Diana"])

    def test_column_not_found(self):
        with self.assertRaises(KeyError):
            self.table.column("nonexistent")

    def test_head(self):
        head = self.table.head(2)
        self.assertEqual(head.num_rows, 2)

    def test_tail(self):
        tail = self.table.tail(2)
        self.assertEqual(tail.num_rows, 2)
        self.assertEqual(tail.column("name")[0], "Charlie")

    def test_select_columns(self):
        selected = self.table.select_columns(["name", "age"])
        self.assertEqual(selected.num_columns, 2)
        self.assertEqual(selected.columns, ["name", "age"])

    def test_filter_rows(self):
        filtered = self.table.filter_rows(lambda r: r["age"] is not None and r["age"] > 26)
        self.assertEqual(filtered.num_rows, 2)

    def test_to_csv(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            path = f.name
        try:
            self.table.to_csv(path)
            with open(path, "r") as f:
                content = f.read()
            self.assertIn("name,age,score", content)
            self.assertIn("Alice", content)
        finally:
            os.unlink(path)

    def test_to_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name
        try:
            self.table.to_json(path)
            with open(path, "r") as f:
                data = json.load(f)
            self.assertEqual(len(data), 4)
            self.assertEqual(data[0]["name"], "Alice")
        finally:
            os.unlink(path)


class TestInferValue(unittest.TestCase):
    """Test value type inference."""

    def test_integer(self):
        self.assertEqual(infer_value("42"), 42)
        self.assertEqual(infer_value("-7"), -7)

    def test_float(self):
        self.assertAlmostEqual(infer_value("3.14"), 3.14)
        self.assertAlmostEqual(infer_value("-0.5"), -0.5)

    def test_boolean(self):
        self.assertIs(infer_value("true"), True)
        self.assertIs(infer_value("false"), False)

    def test_none_values(self):
        self.assertIsNone(infer_value(""))
        self.assertIsNone(infer_value("null"))
        self.assertIsNone(infer_value("N/A"))
        self.assertIsNone(infer_value("NaN"))

    def test_string(self):
        self.assertEqual(infer_value("hello"), "hello")
        self.assertEqual(infer_value("Alice"), "Alice")


class TestInferColumnType(unittest.TestCase):
    """Test column type inference."""

    def test_integer_column(self):
        self.assertEqual(infer_column_type([1, 2, 3, 4, 5]), "integer")

    def test_float_column(self):
        self.assertEqual(infer_column_type([1.1, 2.2, 3.3, 4.4]), "float")

    def test_string_column(self):
        self.assertEqual(infer_column_type(["a", "b", "c", "d"]), "string")

    def test_empty_column(self):
        self.assertEqual(infer_column_type([]), "empty")

    def test_mixed_column(self):
        self.assertEqual(infer_column_type([1, 2, "hello", 4]), "string")


class TestLoadFile(unittest.TestCase):
    """Test file loading."""

    def test_load_csv(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("name,age,score\nAlice,25,85.5\nBob,30,92.0\n")
            path = f.name
        try:
            table = load_file(path)
            self.assertEqual(table.num_rows, 2)
            self.assertEqual(table.num_columns, 3)
            self.assertEqual(table.column("name"), ["Alice", "Bob"])
            self.assertEqual(table.column("age"), [25, 30])
        finally:
            os.unlink(path)

    def test_load_tsv(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False) as f:
            f.write("name\tage\nAlice\t25\nBob\t30\n")
            path = f.name
        try:
            table = load_file(path)
            self.assertEqual(table.num_rows, 2)
            self.assertEqual(table.column("name"), ["Alice", "Bob"])
        finally:
            os.unlink(path)

    def test_load_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}], f)
            path = f.name
        try:
            table = load_file(path)
            self.assertEqual(table.num_rows, 2)
            self.assertEqual(table.column("name"), ["Alice", "Bob"])
        finally:
            os.unlink(path)

    def test_load_jsonl(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write('{"name": "Alice", "age": 25}\n{"name": "Bob", "age": 30}\n')
            path = f.name
        try:
            table = load_file(path)
            self.assertEqual(table.num_rows, 2)
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_file("/nonexistent/file.csv")

    def test_max_rows(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("a,b\n1,2\n3,4\n5,6\n7,8\n")
            path = f.name
        try:
            table = load_file(path, max_rows=2)
            self.assertEqual(table.num_rows, 2)
        finally:
            os.unlink(path)


class TestDetectFormat(unittest.TestCase):
    """Test format detection."""

    def test_csv_extension(self):
        self.assertEqual(detect_format("data.csv"), "csv")

    def test_tsv_extension(self):
        self.assertEqual(detect_format("data.tsv"), "tsv")

    def test_json_extension(self):
        self.assertEqual(detect_format("data.json"), "json")

    def test_jsonl_extension(self):
        self.assertEqual(detect_format("data.jsonl"), "jsonl")


if __name__ == "__main__":
    unittest.main()

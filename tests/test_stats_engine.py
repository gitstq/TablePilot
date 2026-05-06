"""Unit tests for TablePilot statistics engine."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tablepilot.stats_engine import (
    mean, median, mode, std_dev, variance, skewness, kurtosis,
    percentile, min_max, sum_values, cv, count, unique_count,
    descriptive_stats, correlation, detect_outliers_iqr, detect_outliers_zscore,
)


class TestBasicStats(unittest.TestCase):
    """Test basic statistical functions."""

    def test_mean(self):
        self.assertAlmostEqual(mean([1, 2, 3, 4, 5]), 3.0)
        self.assertAlmostEqual(mean([10, 20, 30]), 20.0)
        self.assertIsNone(mean([]))

    def test_median_odd(self):
        self.assertAlmostEqual(median([1, 2, 3, 4, 5]), 3.0)

    def test_median_even(self):
        self.assertAlmostEqual(median([1, 2, 3, 4]), 2.5)
        self.assertIsNone(median([]))

    def test_mode(self):
        self.assertEqual(mode([1, 2, 2, 3, 3, 3]), [3])
        self.assertEqual(mode([1, 1, 2, 2]), [1, 2])
        self.assertEqual(mode([]), [])

    def test_variance(self):
        result = variance([1, 2, 3, 4, 5])
        self.assertAlmostEqual(result, 2.5, places=4)
        self.assertIsNone(variance([1]))

    def test_std_dev(self):
        result = std_dev([1, 2, 3, 4, 5])
        self.assertAlmostEqual(result, 1.5811, places=3)
        self.assertIsNone(std_dev([]))

    def test_percentile(self):
        self.assertAlmostEqual(percentile([1, 2, 3, 4, 5], 50), 3.0)
        self.assertAlmostEqual(percentile([1, 2, 3, 4, 5], 25), 2.0)
        self.assertAlmostEqual(percentile([1, 2, 3, 4, 5], 75), 4.0)
        self.assertIsNone(percentile([], 50))

    def test_min_max(self):
        result = min_max([1, 5, 3, 9, 2])
        self.assertEqual(result["min"], 1)
        self.assertEqual(result["max"], 9)
        self.assertEqual(result["range"], 8)

    def test_sum(self):
        self.assertAlmostEqual(sum_values([1, 2, 3, 4, 5]), 15.0)
        self.assertIsNone(sum_values([]))

    def test_cv(self):
        result = cv([10, 12, 14, 16, 18])
        self.assertIsNotNone(result)
        self.assertIsNone(cv([5, 5, 5]))  # zero std


class TestCountFunctions(unittest.TestCase):
    """Test counting functions."""

    def test_count(self):
        result = count([1, None, 3, None, 5])
        self.assertEqual(result["total"], 5)
        self.assertEqual(result["non_null"], 3)
        self.assertEqual(result["null"], 2)
        self.assertAlmostEqual(result["null_pct"], 40.0)

    def test_unique_count(self):
        result = unique_count([1, 2, 2, 3, 3, 3])
        self.assertEqual(result["unique"], 3)
        self.assertEqual(result["duplicates"], 3)


class TestDescriptiveStats(unittest.TestCase):
    """Test comprehensive descriptive statistics."""

    def test_numeric_stats(self):
        stats = descriptive_stats([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(stats["type"], "numeric")
        self.assertAlmostEqual(stats["mean"], 5.5)
        self.assertAlmostEqual(stats["median"], 5.5)
        self.assertEqual(stats["min"], 1)
        self.assertEqual(stats["max"], 10)

    def test_categorical_stats(self):
        stats = descriptive_stats(["a", "b", "a", "c", "b", "a"])
        self.assertEqual(stats["type"], "categorical")
        self.assertEqual(stats["unique"]["unique"], 3)
        self.assertEqual(len(stats["top_values"]), 3)
        self.assertEqual(stats["top_values"][0]["value"], "a")

    def test_with_nulls(self):
        stats = descriptive_stats([1, None, 3, None, 5])
        self.assertEqual(stats["count"]["null"], 2)
        self.assertEqual(stats["count"]["non_null"], 3)


class TestCorrelation(unittest.TestCase):
    """Test correlation functions."""

    def test_perfect_positive(self):
        result = correlation([1, 2, 3, 4, 5], [2, 4, 6, 8, 10])
        self.assertAlmostEqual(result, 1.0, places=4)

    def test_perfect_negative(self):
        result = correlation([1, 2, 3, 4, 5], [10, 8, 6, 4, 2])
        self.assertAlmostEqual(result, -1.0, places=4)

    def test_no_correlation(self):
        import random
        random.seed(42)
        x = [random.random() for _ in range(100)]
        y = [random.random() for _ in range(100)]
        result = correlation(x, y)
        self.assertTrue(abs(result) < 0.3)

    def test_insufficient_data(self):
        self.assertIsNone(correlation([1, 2], [3, 4]))


class TestOutlierDetection(unittest.TestCase):
    """Test outlier detection."""

    def test_iqr_no_outliers(self):
        result = detect_outliers_iqr([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(result["count"], 0)

    def test_iqr_with_outliers(self):
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]
        result = detect_outliers_iqr(data)
        self.assertGreater(result["count"], 0)
        self.assertIn(100, result["outliers"])

    def test_zscore_no_outliers(self):
        result = detect_outliers_zscore([1, 2, 3, 4, 5])
        self.assertEqual(result["count"], 0)

    def test_zscore_with_outliers(self):
        data = [10, 11, 10, 12, 11, 10, 11, 12, 10, 1000]
        result = detect_outliers_zscore(data, threshold=2.0)
        self.assertGreater(result["count"], 0)


class TestSkewnessKurtosis(unittest.TestCase):
    """Test distribution shape measures."""

    def test_symmetric_distribution(self):
        result = skewness([1, 2, 3, 4, 5])
        self.assertAlmostEqual(result, 0.0, places=1)

    def test_right_skewed(self):
        result = skewness([1, 2, 3, 4, 100])
        self.assertGreater(result, 0)

    def test_kurtosis_normal_like(self):
        # Normal distribution has kurtosis ≈ 0 (excess)
        import random
        random.seed(42)
        data = [random.gauss(0, 1) for _ in range(1000)]
        result = kurtosis(data)
        self.assertAlmostEqual(result, 0.0, places=1)


if __name__ == "__main__":
    unittest.main()

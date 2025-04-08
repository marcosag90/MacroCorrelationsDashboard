import unittest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.data_processing.correlation import (
    normalize_series,
    calculate_average_correlation,
    multi_timeframe_sliding_correlation,
    calculate_fixed_window_correlation
)

class TestCorrelation(unittest.TestCase):
    def setUp(self):
        """Setup test data"""
        dates = pd.date_range(start='2020-01-01', end='2020-12-31', freq='D')
        self.price_data = pd.DataFrame({
            'close': np.random.normal(100, 10, len(dates)),
            'open': np.random.normal(100, 10, len(dates)),
            'high': np.random.normal(105, 10, len(dates)),
            'low': np.random.normal(95, 10, len(dates)),
        }, index=dates)
        
        self.btc_data = pd.DataFrame({
            'close': np.random.normal(10000, 1000, len(dates)),
            'open': np.random.normal(10000, 1000, len(dates)),
            'high': np.random.normal(10500, 1000, len(dates)),
            'low': np.random.normal(9500, 1000, len(dates)),
        }, index=dates)
        
        # Create uppercase column name variants
        self.price_data_upper = pd.DataFrame({
            'Close': self.price_data['close'].values,
            'Open': self.price_data['open'].values,
            'High': self.price_data['high'].values,
            'Low': self.price_data['low'].values
        }, index=dates)
        
        self.btc_data_upper = pd.DataFrame({
            'Close': self.btc_data['close'].values,
            'Open': self.btc_data['open'].values,
            'High': self.btc_data['high'].values,
            'Low': self.btc_data['low'].values
        }, index=dates)
        
        # Create data with non-standard column names
        self.price_data_custom = pd.DataFrame({
            'price': self.price_data['close'].values,
            'start': self.price_data['open'].values,
            'max': self.price_data['high'].values,
            'min': self.price_data['low'].values
        }, index=dates)
        
        self.btc_data_custom = pd.DataFrame({
            'price': self.btc_data['close'].values,
            'start': self.btc_data['open'].values,
            'max': self.btc_data['high'].values,
            'min': self.btc_data['low'].values
        }, index=dates)
        
        # Create non-numeric data
        self.non_numeric_data = pd.DataFrame({
            'date': [str(d) for d in dates],
            'status': ['active' for _ in range(len(dates))]
        }, index=dates)
        
        self.assets_dict = {
            'GOLD': self.price_data.copy(),
            'SPX': self.price_data.copy() * 1.5,
            'VIX': self.price_data.copy() * 0.5
        }

    def test_normalize_series(self):
        """Test series normalization"""
        series = pd.Series([1, 2, 3, 4, 5])
        normalized = normalize_series(series)
        self.assertEqual(normalized.min(), 0)
        self.assertEqual(normalized.max(), 1)
        self.assertEqual(len(normalized), len(series))

    def test_calculate_average_correlation(self):
        """Test average correlation calculation"""
        windows = [15, 30, 60]
        avg_corr = calculate_average_correlation(self.price_data, self.btc_data, windows)
        
        self.assertIsInstance(avg_corr, pd.Series)
        self.assertFalse(avg_corr.empty)

    def test_calculate_fixed_window_correlation(self):
        """Test fixed window correlation calculation"""
        window = 30
        corr = calculate_fixed_window_correlation(self.price_data, self.btc_data, window)
        
        # Check type and value range
        self.assertIsInstance(corr, float)
        self.assertGreaterEqual(corr, -1)
        self.assertLessEqual(corr, 1)

    def test_multi_timeframe_sliding_correlation_detailed(self):
        """Test multi-timeframe correlation calculation with fixed windows"""
        windows = [15, 30, 60]
        avg_correlations = multi_timeframe_sliding_correlation(self.assets_dict, self.btc_data, windows)
        
        # Check structure
        self.assertIsInstance(avg_correlations, dict)
        self.assertEqual(set(avg_correlations.keys()), set(self.assets_dict.keys()))
        
        # Check correlations for each asset
        for symbol, correlations in avg_correlations.items():
            self.assertIsInstance(correlations, pd.Series)
            self.assertEqual(set(correlations.index), set(windows))
            for corr in correlations:
                self.assertGreaterEqual(corr, -1)
                self.assertLessEqual(corr, 1)

    def test_multi_timeframe_sliding_correlation(self):
        """Test multi-timeframe correlation calculation"""
        windows = [15, 30, 60]
        result = multi_timeframe_sliding_correlation(self.assets_dict, self.btc_data, windows)
        
        # This test needs to be updated as multi_timeframe_sliding_correlation now returns a different structure
        self.assertIsInstance(result, dict)
        
        # Check correlations structure
        for symbol in self.assets_dict.keys():
            self.assertIn(symbol, result)
            corr_series = result[symbol]
            self.assertIsInstance(corr_series, pd.Series)
            for val in corr_series.values:
                self.assertGreaterEqual(val, -1)
                self.assertLessEqual(val, 1)

    def test_calculate_fixed_window_correlation_uppercase(self):
        """Test fixed window correlation calculation with uppercase column names"""
        window = 30
        # Test with uppercase column names
        corr = calculate_fixed_window_correlation(self.price_data_upper, self.btc_data_upper, window)
        
        # Check type and value range
        self.assertIsInstance(corr, float)
        self.assertGreaterEqual(corr, -1)
        self.assertLessEqual(corr, 1)

    def test_calculate_fixed_window_correlation_custom_columns(self):
        """Test fixed window correlation calculation with non-standard column names"""
        window = 30
        # Test with custom column names, should use first numeric column
        corr = calculate_fixed_window_correlation(self.price_data_custom, self.btc_data_custom, window)
        
        # Check type and value range
        self.assertIsInstance(corr, float)
        self.assertGreaterEqual(corr, -1)
        self.assertLessEqual(corr, 1)

    def test_calculate_fixed_window_correlation_error(self):
        """Test error when no numeric columns are found"""
        window = 30
        # Test with non-numeric data, should raise ValueError
        with self.assertRaises(ValueError):
            calculate_fixed_window_correlation(self.non_numeric_data, self.non_numeric_data, window)
    
    def test_mixed_column_names(self):
        """Test correlation calculation with mixed column name casing"""
        window = 30
        # Test with mixed case (lowercase and uppercase)
        corr = calculate_fixed_window_correlation(self.price_data, self.btc_data_upper, window)
        
        # Check type and value range
        self.assertIsInstance(corr, float)
        self.assertGreaterEqual(corr, -1)
        self.assertLessEqual(corr, 1)

    def test_validate_price_dataframe(self):
        """Test validation of price dataframes"""
        # These should pass
        from src.data_processing.correlation import validate_price_dataframe
        validate_price_dataframe(self.price_data)
        validate_price_dataframe(self.price_data_upper)
        validate_price_dataframe(self.price_data_custom)
        
        # This should fail
        with self.assertRaises(ValueError):
            validate_price_dataframe(self.non_numeric_data)
            
        # Test with wrong type
        with self.assertRaises(TypeError):
            validate_price_dataframe("not a dataframe")
            
    def test_get_price_series(self):
        """Test extracting price series from different dataframe formats"""
        from src.data_processing.correlation import get_price_series
        
        # Test with lowercase 'close'
        series1 = get_price_series(self.price_data)
        self.assertIsInstance(series1, pd.Series)
        self.assertTrue((series1 == self.price_data['close']).all())
        
        # Test with uppercase 'Close'
        series2 = get_price_series(self.price_data_upper)
        self.assertIsInstance(series2, pd.Series)
        self.assertTrue((series2 == self.price_data_upper['Close']).all())
        
        # Test with custom columns
        series3 = get_price_series(self.price_data_custom)
        self.assertIsInstance(series3, pd.Series)
        # Should pick the first numeric column
        self.assertTrue((series3 == self.price_data_custom['price']).all())


if __name__ == '__main__':
    unittest.main()
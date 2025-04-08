import unittest
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.datafeed.datafeed import TradingViewDataFeed, DataInterval

class TestDatafeed(unittest.TestCase):
    
    def setUp(self):
        """Setup test data and mocks"""
        # Create a sample DataFrame that mimics TradingView data
        dates = pd.date_range(start='2020-01-01', end='2020-01-10', freq='D')
        self.mock_data = pd.DataFrame({
            'open': np.random.normal(100, 10, len(dates)),
            'high': np.random.normal(105, 10, len(dates)),
            'low': np.random.normal(95, 10, len(dates)),
            'close': np.random.normal(100, 10, len(dates)),
            'volume': np.random.randint(1000, 100000, len(dates))
        }, index=dates)
    
    @patch('src.datafeed.datafeed.TvDatafeed')
    def test_init(self, mock_tv_datafeed):
        """Test initialization of TradingViewDataFeed"""
        # Setup the mock
        mock_instance = Mock()
        mock_tv_datafeed.return_value = mock_instance
        
        # Create an instance of TradingViewDataFeed
        feed = TradingViewDataFeed(
            asset="INDEX:BTCUSD", 
            interval=DataInterval.ONE_DAY, 
            since="2020-01-01"
        )
        
        # Assert properties are set correctly
        self.assertEqual(feed.asset, "INDEX:BTCUSD")
        self.assertEqual(feed.interval, DataInterval.ONE_DAY)
        self.assertEqual(feed.since, "2020-01-01")
        self.assertIsNone(feed.data)
        
        # Assert TvDatafeed was initialized
        mock_tv_datafeed.assert_called_once()
    
    @patch('src.datafeed.datafeed.TvDatafeed')
    def test_get_data_first_time(self, mock_tv_datafeed):
        """Test get_data method when called for the first time"""
        # Setup the mock
        mock_instance = Mock()
        mock_instance.get_hist.return_value = self.mock_data
        mock_tv_datafeed.return_value = mock_instance
        
        # Create an instance and call get_data
        feed = TradingViewDataFeed(
            asset="INDEX:BTCUSD",
            interval=DataInterval.ONE_DAY,
            since="2020-01-01"
        )
        result = feed.get_data()
        
        # Assert get_hist was called with proper params
        days_diff = (datetime.now() - datetime(2020, 1, 1)).days
        mock_instance.get_hist.assert_called_once_with(
            symbol="INDEX:BTCUSD",
            interval=DataInterval.ONE_DAY.value,
            n_bars=days_diff
        )
        
        # Assert result is the mock data and data is cached
        self.assertIs(result, self.mock_data)
        self.assertIs(feed.data, self.mock_data)
    
    @patch('src.datafeed.datafeed.TvDatafeed')
    def test_get_data_cached(self, mock_tv_datafeed):
        """Test get_data method when data is already cached"""
        # Setup the mock
        mock_instance = Mock()
        mock_instance.get_hist.return_value = self.mock_data
        mock_tv_datafeed.return_value = mock_instance
        
        # Create an instance and set data directly
        feed = TradingViewDataFeed(
            asset="INDEX:BTCUSD",
            interval=DataInterval.ONE_DAY,
            since="2020-01-01"
        )
        feed.data = self.mock_data
        
        # Call get_data and assert get_hist was NOT called
        result = feed.get_data()
        mock_instance.get_hist.assert_not_called()
        
        # Assert result is the cached data
        self.assertIs(result, self.mock_data)
    
    @patch('src.datafeed.datafeed.TvDatafeed')
    def test_get_data_without_since(self, mock_tv_datafeed):
        """Test get_data method when since is not provided"""
        # Setup the mock
        mock_instance = Mock()
        mock_instance.get_hist.return_value = self.mock_data
        mock_tv_datafeed.return_value = mock_instance
        
        # Create an instance without since and call get_data
        feed = TradingViewDataFeed(
            asset="INDEX:BTCUSD",
            interval=DataInterval.ONE_DAY
        )
        result = feed.get_data()
        
        # Assert get_hist was called with default n_bars
        mock_instance.get_hist.assert_called_once_with(
            symbol="INDEX:BTCUSD",
            interval=DataInterval.ONE_DAY.value,
            n_bars=2000
        )
        
        # Assert result is the mock data
        self.assertIs(result, self.mock_data)
    
    def test_data_interval_enum(self):
        """Test DataInterval enum values"""
        from tvDatafeed import Interval
        
        # Verify the enum values
        self.assertEqual(DataInterval.ONE_DAY.value, Interval.in_daily)
        self.assertEqual(DataInterval.ONE_WEEK.value, Interval.in_weekly)
        self.assertEqual(DataInterval.ONE_MONTH.value, Interval.in_monthly)
        
if __name__ == '__main__':
    unittest.main()

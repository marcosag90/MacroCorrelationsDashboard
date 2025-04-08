import unittest
import os
import sys
import tempfile
import yaml
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.config.readConfig import read_config, MacroTicker

class TestConfigReader(unittest.TestCase):
    def setUp(self):
        """Setup test data and temporary files"""
        self.valid_yaml_data = {
            "tickers": [
                {"ticker": "INDEX:BTCUSD", "frequency": "D"},
                {"ticker": "INDEX:ETHUSD", "frequency": "W"},
                {"ticker": "CRYPTO:SOLUSD", "frequency": "M"}
            ]
        }
        
        self.empty_yaml_data = {}
        
        self.incomplete_yaml_data = {
            "tickers": [
                {"ticker": "INDEX:BTCUSD", "frequency": "D"},
                {"ticker": "INDEX:ETHUSD"}, # Missing frequency
                {"frequency": "M"} # Missing ticker
            ]
        }
        
        # Create temporary files
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Valid YAML file
        self.valid_config_path = os.path.join(self.temp_dir.name, "valid_config.yaml")
        with open(self.valid_config_path, 'w') as f:
            yaml.dump(self.valid_yaml_data, f)
        
        # Empty YAML file
        self.empty_config_path = os.path.join(self.temp_dir.name, "empty_config.yaml")
        with open(self.empty_config_path, 'w') as f:
            yaml.dump(self.empty_yaml_data, f)
        
        # Incomplete YAML file
        self.incomplete_config_path = os.path.join(self.temp_dir.name, "incomplete_config.yaml")
        with open(self.incomplete_config_path, 'w') as f:
            yaml.dump(self.incomplete_yaml_data, f)
        
        # Non-existent file path
        self.nonexistent_path = os.path.join(self.temp_dir.name, "nonexistent.yaml")
    
    def tearDown(self):
        """Clean up temporary files"""
        self.temp_dir.cleanup()
    
    def test_read_valid_config(self):
        """Test reading a valid YAML config file"""
        tickers = read_config(self.valid_config_path)
        
        # Check the result structure
        self.assertIsInstance(tickers, list)
        self.assertEqual(len(tickers), 3)
        
        # Check individual ticker objects
        self.assertEqual(tickers[0].symbol, "INDEX:BTCUSD")
        self.assertEqual(tickers[0].frequency, "D")
        self.assertEqual(tickers[1].symbol, "INDEX:ETHUSD")
        self.assertEqual(tickers[1].frequency, "W")
        self.assertEqual(tickers[2].symbol, "CRYPTO:SOLUSD")
        self.assertEqual(tickers[2].frequency, "M")
    
    def test_read_empty_config(self):
        """Test reading an empty YAML config file"""
        tickers = read_config(self.empty_config_path)
        
        # Should return an empty list
        self.assertIsInstance(tickers, list)
        self.assertEqual(len(tickers), 0)
    
    def test_read_incomplete_config(self):
        """Test reading a YAML config with missing fields"""
        tickers = read_config(self.incomplete_config_path)
        
        # Should still return 3 tickers, but with None for missing values
        self.assertIsInstance(tickers, list)
        self.assertEqual(len(tickers), 3)
        self.assertEqual(tickers[0].symbol, "INDEX:BTCUSD")
        self.assertEqual(tickers[0].frequency, "D")
        self.assertEqual(tickers[1].symbol, "INDEX:ETHUSD")
        self.assertIsNone(tickers[1].frequency)
        self.assertIsNone(tickers[2].symbol)
        self.assertEqual(tickers[2].frequency, "M")
    
    def test_read_nonexistent_config(self):
        """Test reading a non-existent file (should raise FileNotFoundError)"""
        with self.assertRaises(FileNotFoundError):
            read_config(self.nonexistent_path)
    
    def test_macro_ticker_dataclass(self):
        """Test MacroTicker dataclass functionality"""
        ticker = MacroTicker(symbol="TEST:SYMBOL", frequency="D")
        
        self.assertEqual(ticker.symbol, "TEST:SYMBOL")
        self.assertEqual(ticker.frequency, "D")
        
        # Test equality of two identical tickers
        ticker2 = MacroTicker(symbol="TEST:SYMBOL", frequency="D")
        self.assertEqual(ticker, ticker2)
        
        # Test inequality
        ticker3 = MacroTicker(symbol="OTHER:SYMBOL", frequency="D")
        self.assertNotEqual(ticker, ticker3)


if __name__ == '__main__':
    unittest.main()

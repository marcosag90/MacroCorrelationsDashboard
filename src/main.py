from config.readConfig import read_config, MacroTicker
from datafeed.datafeed import TradingViewDataFeed, DataInterval
from data_processing.correlation import multi_timeframe_sliding_correlation 
import streamlit as st
from typing import List, Dict, Any
import pandas as pd

def parse_interval(frequency: str):
    """
    Parses the frequency string and returns the corresponding DataInterval enum value.
    
    :param frequency: Frequency string (e.g., "D", "W", "M").
    :return: DataInterval enum value.
    """
    frequency_map = {
        "D": DataInterval.ONE_DAY,
        "W": DataInterval.ONE_WEEK,
        "M": DataInterval.ONE_MONTH
    }
    return frequency_map[frequency] if frequency in frequency_map else None

def process_market_data() -> Dict[str, Any]:
    """Process market data and calculate correlations"""
    # Read configuration
    config = read_config('MacroTickers.yaml')
    
    # Create TradingViewDataFeed instances for each ticker
    data_feed = [TradingViewDataFeed(asset=ticker.symbol, interval=parse_interval(ticker.frequency), since="2017-12-31") for ticker in config]
    raw_data = {}
    for ticker, feed in zip(config, data_feed):
        raw_data[ticker.symbol] = feed.get_data()
    
    # Fetch Bitcoin data to compare against
    bitcoin_feed = TradingViewDataFeed(asset="INDEX:BTCUSD", interval=DataInterval.ONE_DAY, since="2017-12-31")
    bitcoin_data = bitcoin_feed.get_data()
    
    # Calculate correlations
    correlation_data = {}
    timeframes = [15, 30, 60, 90]
    
    for ticker in config:
        # Create a single-item dictionary for each asset to match the function's expected input
        asset_dict = {ticker.symbol: raw_data[ticker.symbol]}
        result = multi_timeframe_sliding_correlation(
            asset_dict,  # Pass a dictionary with a single asset
            bitcoin_data, 
            timeframes
        )
        # The result is a dict with one entry, extract just the Series
        correlation_data[ticker.symbol] = result[ticker.symbol]
    
    return {
        "config": config,
        "raw_data": raw_data,
        "bitcoin_data": bitcoin_data,
        "correlation_data": correlation_data
    }

def main():
    # Initialize session state if not already done
    if 'market_data' not in st.session_state:
        st.session_state.market_data = process_market_data()
    
    indicator_options = {
        "Quant Research": [
            st.Page("views/1_Macro_Correlations.py", title="Macro Correlations", default=True), 
        ]
    }
    
    pg = st.navigation(indicator_options)
    pg.run()

if __name__ == "__main__":
    main()

import pandas as pd
import numpy as np
from typing import Dict, List, Union, Tuple, cast

# Define the expected data structure type
PriceDataFrame = pd.DataFrame  # DataFrame with required price columns
CorrelationResult = Dict[str, pd.Series]  # Dictionary of correlation series

def validate_price_dataframe(df: pd.DataFrame, name: str = "dataframe") -> None:
    """Validate that the DataFrame has the expected price data structure."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected {name} to be a pandas DataFrame, got {type(df).__name__}")
    
    if 'close' not in df.columns and 'Close' not in df.columns:
        # Try to find numeric columns
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) == 0:
            raise ValueError(f"{name} must contain a 'close', 'Close', or at least one numeric column")

def get_price_series(df: pd.DataFrame) -> pd.Series:
    """Extract the price series from a DataFrame consistently.
    
    Priority: 'close' column, 'Close' column, first numeric column.
    """
    validate_price_dataframe(df)
    
    if 'close' in df.columns:
        return df['close']
    elif 'Close' in df.columns:
        return df['Close']
    else:
        # Get the first numeric column
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        return df[numeric_cols[0]]

def normalize_series(series: pd.Series) -> pd.Series:
    """Normalize series to 0-1 range for better visual comparison"""
    return (series - series.min()) / (series.max() - series.min())

def calculate_fixed_window_correlation(asset_data: pd.DataFrame, btc_data: pd.DataFrame, window: int) -> float:
    """Calculate correlation between asset and BTC over the last fixed window of days.
    
    Parameters:
        asset_data: DataFrame containing price data for the asset
        btc_data: DataFrame containing price data for Bitcoin
        window: Number of days to include in the correlation window
        
    Returns:
        Correlation coefficient as a float
    """
    # Validate inputs
    validate_price_dataframe(asset_data, "asset_data")
    validate_price_dataframe(btc_data, "btc_data")
    
    # Extract price series
    asset_series = get_price_series(asset_data)
    btc_series = get_price_series(btc_data)
    
    # Calculate correlation using window
    asset_window = asset_series.iloc[-window:]
    btc_window = btc_series.iloc[-window:]
    return asset_window.corr(btc_window)

def calculate_average_correlation(asset_data: pd.DataFrame, btc_data: pd.DataFrame, windows: List[int]) -> pd.Series:
    """Calculate average correlation across all fixed windows for a single asset.
    
    Parameters:
        asset_data: DataFrame containing price data for the asset
        btc_data: DataFrame containing price data for Bitcoin
        windows: List of window sizes to calculate correlations for
        
    Returns:
        Series of correlations indexed by window size
    """
    # Validate inputs
    validate_price_dataframe(asset_data, "asset_data")
    validate_price_dataframe(btc_data, "btc_data")
    
    correlations = {}
    for window in windows:
        corr = calculate_fixed_window_correlation(asset_data, btc_data, window)
        correlations[window] = corr
    return pd.Series(correlations)

def multi_timeframe_sliding_correlation(
    assets_dict: Dict[str, pd.DataFrame], 
    btc_data: pd.DataFrame, 
    windows: List[int]
) -> Dict[str, pd.Series]:
    """Calculate correlations for all assets over fixed windows.
    
    Parameters:
        assets_dict: Dictionary mapping asset symbols to their price DataFrames
        btc_data: DataFrame containing price data for Bitcoin
        windows: List of window sizes to calculate correlations for
        
    Returns:
        Dictionary mapping asset symbols to their correlation series
    """
    # Validate Bitcoin data
    validate_price_dataframe(btc_data, "btc_data")
    
    avg_correlations: Dict[str, pd.Series] = {}
    
    # Calculate correlation for each asset
    for symbol, asset_data in assets_dict.items():
        # Validate each asset's data
        validate_price_dataframe(asset_data, f"assets_dict[{symbol}]")
        
        avg_corr = calculate_average_correlation(asset_data, btc_data, windows)
        avg_correlations[symbol] = avg_corr
    
    return avg_correlations
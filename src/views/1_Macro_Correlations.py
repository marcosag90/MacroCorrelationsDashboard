import streamlit as st
from streamlit_lightweight_charts import renderLightweightCharts
import pandas as pd

def create_price_chart(btc_series, asset_series, symbol):
    """Create price comparison chart configuration"""
    # Normalize both series
    btc_norm = (btc_series - btc_series.min()) / (btc_series.max() - btc_series.min())
    asset_norm = (asset_series - asset_series.min()) / (asset_series.max() - asset_series.min())
    
    btc_data = [{"time": str(idx.date()), "value": float(val)} 
                for idx, val in btc_norm.items() if pd.notna(val)]
    asset_data = [{"time": str(idx.date()), "value": float(val)} 
                  for idx, val in asset_norm.items() if pd.notna(val)]
    
    return [
        {
            "name": "BTC",
            "type": "line",
            "data": btc_data,
            "color": "orange",
            "lineWidth": 2,
        },
        {
            "name": symbol,
            "type": "line",
            "data": asset_data,
            "color": "blue",
            "lineWidth": 2,
        }
    ]

def create_multi_asset_chart(btc_series, assets_dict):
    """Create chart with Bitcoin in orange and all other assets in light gray"""
    # Normalize BTC series
    btc_norm = (btc_series - btc_series.min()) / (btc_series.max() - btc_series.min())
    
    btc_data = [{"time": str(idx.date()), "value": float(val)} 
                for idx, val in btc_norm.items() if pd.notna(val)]
    
    # Start with BTC series
    series_list = [{
        "type": "Line",
        "data": btc_data,
        "options": {
            "title": "Bitcoin",
            "color": "orange",
            "lineWidth": 2,
            "priceScaleId": "right"
        }
    }]
    
    # Add all other assets in light gray
    for symbol, asset_df in assets_dict.items():
        if symbol == "INDEX:BTCUSD":
            continue  # Skip Bitcoin as it's already added
            
        # Get close price column (handle different possible column names)
        if 'close' in asset_df.columns:
            price_col = 'close'
        elif 'Close' in asset_df.columns:
            price_col = 'Close'
        else:
            # Use first numeric column if standard names not found
            numeric_cols = asset_df.select_dtypes(include=['float64', 'int64']).columns
            if len(numeric_cols) > 0:
                price_col = numeric_cols[0]
            else:
                continue  # Skip this asset if no suitable column found
        
        # Normalize asset series
        asset_series = asset_df[price_col]
        asset_norm = (asset_series - asset_series.min()) / (asset_series.max() - asset_series.min())
        
        asset_data = [{"time": str(idx.date()), "value": float(val)} 
                      for idx, val in asset_norm.items() if pd.notna(val)]
        
        series_list.append({
            "type": "Line",
            "data": asset_data,
            "options": {
                "title": symbol,
                "color": "lightgray",
                "lineWidth": 1,
                "priceScaleId": "right"
            }
        })
    
    return series_list

def create_correlation_chart(correlations_dict):
    """Create correlation comparison chart configuration"""
    series_list = []
    for symbol, series in correlations_dict.items():
        data = [{"time": str(window), "value": float(val)} 
                for window, val in series.items() if pd.notna(val)]
        
        series_list.append({
            "type": "Line",
            "data": data,
            "options": {
                "title": symbol,
                "lineWidth": 2,
                "priceScaleId": "right"
            }
        })
    return series_list

# Set the title of the app
st.title("Macro Correlations Dashboard")

# Access cached data
market_data = st.session_state.market_data
bitcoin_data = market_data["bitcoin_data"]
raw_data = market_data["raw_data"]
correlation_data = market_data["correlation_data"]

# Create two columns for side-by-side charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Asset Correlations with Bitcoin")
    # Display correlation chart on the left
    correlation_chart_options = {
        "layout": {
            "textColor": "black",
            "background": {
                "type": "solid",
                "color": "white"
            }
        },
        "rightPriceScale": {
            "scaleMargins": {"top": 0.1, "bottom": 0.1},
            "minimumValue": -1,
            "maximumValue": 1,
            "visible": True
        },
        "timeScale": {
            "timeVisible": True,
            "secondsVisible": False,
        }
    }
    
    renderLightweightCharts([
        {
            "chart": correlation_chart_options,
            "series": create_correlation_chart(correlation_data)
        }
    ], 'correlation_chart')

with col2:
    st.subheader("Bitcoin vs Other Assets Price Chart")
    # Display Bitcoin with all other assets overlaid on the right
    price_chart_options = {
        "layout": {
            "textColor": "black",
            "background": {
                "type": "solid",
                "color": "white"
            }
        },
        "rightPriceScale": {
            "scaleMargins": {"top": 0.1, "bottom": 0.1},
            "visible": True
        },
        "timeScale": {
            "timeVisible": True,
            "secondsVisible": False,
        }
    }
    
    renderLightweightCharts([
        {
            "chart": price_chart_options,
            "series": create_multi_asset_chart(bitcoin_data['close'] if 'close' in bitcoin_data.columns else bitcoin_data.iloc[:, 0], raw_data)
        }
    ], 'price_chart')

# Add explanation below the charts
st.markdown("""
### Chart Explanation
- **Left Chart:** Shows the correlation levels between Bitcoin and different assets across various timeframes
- **Right Chart:** Displays normalized price movements of Bitcoin (orange) overlaid with all other assets (gray)
""")
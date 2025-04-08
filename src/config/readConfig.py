import yaml
from typing import List
from dataclasses import dataclass

@dataclass
class MacroTicker:
    """
    Data class representing a macro ticker.

    :param symbol: The ticker symbol.
    :param frequency: The frequency of the data (e.g., "D", "W", "M").
    """
    symbol: str
    frequency: str
    
    

def read_config(file_path: str) -> List[MacroTicker]:
    """
    Reads a YAML configuration file and returns a list of MacroTicker objects.

    :param file_path: Path to the YAML configuration file.
    :return: List of MacroTicker objects.
    """
    with open(file_path, 'r') as file:
        config_data = yaml.safe_load(file)

    tickers = []
    for item in config_data.get('tickers', []):
        tickers.append(MacroTicker(
            symbol=item.get('ticker'),
            frequency=item.get('frequency')
        ))

    return tickers
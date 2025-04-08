from tvDatafeed import TvDatafeed, Interval
import pandas as pd
from enum import Enum
from datetime import datetime

class DataInterval(Enum):
    ONE_DAY = Interval.in_daily
    ONE_WEEK = Interval.in_weekly
    ONE_MONTH = Interval.in_monthly

class TradingViewDataFeed:
    def __init__(self, asset: str, interval: DataInterval, since: str = None):
        self.asset = asset
        self.interval = interval
        self.tv = TvDatafeed()
        self.since = since
        self.data = None
        
    def get_data(self) -> pd.DataFrame:
        if(self.data is None):
            n_bars = (datetime.now() - datetime.strptime(self.since, "%Y-%m-%d")).days if self.since else 2000
            self.data = self.tv.get_hist(symbol=self.asset, interval=self.interval.value, n_bars=n_bars)
        return self.data
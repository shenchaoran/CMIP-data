import json
from CMIP import *
class LPJ:
    daily_cols = []
    annual_cols = daily_cols
    month_cols = daily_cols
    def __init__(self, time):
        self.time = time
        self.name = 'LPJ'
        with open('LPJ-daily-cols.json') as f3:
            daily_cols = json.load(f3)
        annual_cols = daily_cols
        month_cols = daily_cols

    @property
    def cols(self):
        if self.time == 'annual':
            return LPJ.annual_cols
        elif self.time == 'month':
            return LPJ.month_cols
        elif self.time == 'daily':
            return LPJ.daily_cols
    
    @property
    def to_month_usecols(self):
        return np.arange(len(LPJ.daily_cols))
    
    @property
    def folder(self):
        return DATA_HOME + '/LPJ/5b9012e4c29ca433443dcfab/outputs'
    
    @property
    def suffix(self):
        if self.time == 'daily':
            return '.daily.csv'
        elif self.time == 'month':
            return '.month.csv'

    def getCol(self, metricName):
        return next(item for item in self.cols if item['metricName'] == metricName)

    def annual_max(self, feature):
        d = {
            'daily-average-GPP': 1.43,
            'daily-average-NPP': 0.786
        }
        return d[feature]

    def annual_min(self, feature):
        return 0
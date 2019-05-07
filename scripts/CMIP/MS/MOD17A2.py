import json
from CMIP import *

class MOD17A2:
    daily_cols = []
    annual_cols = []
    month_cols = []
    def __init__(self, time):
        self.time = time
        self.name = 'MOD17A2'
        with open('MOD17A2-cols.json') as f3:
            daily_cols = json.load(f3)
        annual_cols = daily_cols
        month_cols = daily_cols

    @property
    def cols(self):
        if self.time == 'annual':
            return MOD17A2.annual_cols
        elif self.time == 'month':
            return MOD17A2.month_cols
        elif self.time == 'daily':
            return MOD17A2.daily_cols

    def getCol(self, metricName):
        return next(item for item in self.cols if item['metricName'] == metricName)

    def annual_max(self, feature):
        d = {
            'daily-average-GPP': 3.25
        }
        return d[feature]

    def annual_min(self, feature):
        return 0
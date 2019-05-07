import json
from CMIP import *
class Biome_BGC:
    daily_cols = []
    annual_cols = []
    month_cols = []
    def __init__(self, time):
        self.time = time
        self.name = 'Biome-BGC'
        with open('Biome_BGC-daily-cols.json', 'r') as f:
            daily_cols = json.load(f)
            annual_cols = daily_cols
            month_cols = daily_cols

    @property
    def cols(self):
        if self.time == 'annual':
            return Biome_BGC.annual_cols
        elif self.time == 'month':
            return Biome_BGC.month_cols
        elif self.time == 'daily':
            return Biome_BGC.daily_cols
    
    @property
    def to_month_usecols(self):
        return np.arange(len(self.cols))

    @property
    def folder(self):
        return DATA_HOME + '/Biome_BGC_Data/5b9012e4c29ca433443dcfab/outputs'
    
    @property
    def suffix(self):
        if self.time == 'daily':
            return '.daily.ascii'
        if self.time == 'month':
            return '.month.ascii'
        elif self.time == 'annual':
            return '.annual-avg.ascii'

    def getCol(self, metricName):
        return next(item for item in self.cols if item['metricName'] == metricName)

    def annual_max(self, feature):
        d = {
            'daily-average-GPP': 2.68,
            'daily-average-NPP': 0.5,
            'daily-average-NEP': 0.035,
            'daily-average-NEE': 0.023
        }
        return d[feature]

    def annual_min(self, feature):
        if feature == 'daily-average-NEE':
            return -0.0026
        else:
            return 0

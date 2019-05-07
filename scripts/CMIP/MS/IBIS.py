import json
from CMIP import *
class IBIS:
    # 此处unit为模型输出数据的单位
    # scale 为从模型输出单位转为metric单位的缩放因子
    daily_cols = []
    month_cols = []
    annual_cols = []
    original_annual_cols = []
    lishihua_cols = []
    def __init__(self, time):
        self.time = time
        if self.time == 'lishihua':
            self.name = 'IBIS-lishihua'
        else:
            self.name = 'IBIS'
        with open('IBIS-daily-cols.json') as f1:
            daily_cols = json.load(f1)
        with open('IBIS-lishihua-cols.json') as f2:
            lishihua_cols = json.load(f2)
        with open('IBIS-original-annual-cols.json') as f3:
            original_annual_cols = json.load(f3)
        month_cols = daily_cols[3:]
        annual_cols = month_cols

    @property
    def cols(self):
        if self.time == 'annual':
            return IBIS.annual_cols
        elif self.time == 'month':
            return IBIS.month_cols
        elif self.time == 'daily':
            return IBIS.daily_cols
        elif self.time == 'original-annual':
            return IBIS.original_annual_cols
        elif self.time == 'lishihua':
            return IBIS.lishihua_cols
    
    @property
    def to_month_usecols(self):
        return np.arange(len(IBIS.month_cols))
    
    @property
    def folder(self):
        if self.time == 'lishihua':
            return DATA_HOME + '/IBIS_Data/5b9012e4c29ca433443dcfab/lishihua/Output/correct'
        else:
            return DATA_HOME + '/IBIS_Data/5b9012e4c29ca433443dcfab/outputs'
    
    @property
    def suffix(self):
        if self.time == 'original-annual':
            return '.annual.txt'
        elif self.time == 'lishihua':
            return '.txt'
        else:
            return '.%s.txt' % self.time

    def getCol(self, metricName):
        return next(item for item in self.cols if item['metricName'] == metricName)

    def annual_max(self, feature):
        d = {
            'daily-average-GPP': 4.5,
            'daily-average-NPP': 1,
            'daily-average-NEE': 0.079
        }
        return d[feature]

    def annual_min(self, feature):
        if feature == 'daily-average-NEE':
            return -0.107
        return 0
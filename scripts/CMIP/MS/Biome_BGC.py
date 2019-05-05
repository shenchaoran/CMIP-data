from CMIP import *
class Biome_BGC:
    daily_cols = [
        {
            "id": "soil-respiration",
            "type": "",
            "description": "",
            "scale": 1000.0,
            "offset": 0.0,
            "unit": "kgW m-2 d-1",
            "metricName": "daily-accumulated-co2-respiration-from-soil(total)"
        }, {
            "id": "proj_lai",
            "type": "",
            "description": "",
            "scale": 1.0,
            "offset": 0.0,
            "unit": "1",
            "metricName": "proj_lai"
        }, {
            "id": "all_lai",
            "type": "",
            "description": "",
            "scale": 1.0,
            "offset": 0.0,
            "unit": "1",
            "metricName": "all_lai"
        }, {
            "id": "daily-average-NPP",
            "metricName": "daily-average-NPP",
            "scale": 1000.0,
            "offset": 0.0,
            "type": "number[]",
            "description": "",
            "unit": "kgC m-2 d-1"
        }, {
            "id": "daily-average-NEP",
            "metricName": "daily-average-NEP",
            "scale": 1000.0,
            "offset": 0.0,
            "type": "number[]",
            "description": "",
            "unit": "kgC m-2 d-1"
        }, {
            "id": "daily-average-NEE",
            "metricName": "daily-average-NEE",
            "scale": 1000.0,
            "offset": 0.0,
            "type": "number[]",
            "description": "",
            "unit": "kgC m-2 d-1"
        }, {
            "id": "daily-average-GPP",
            "metricName": "daily-average-GPP",
            "scale": 1000.0,
            "offset": 0.0,
            "type": "number[]",
            "description": "",
            "unit": "kgC m-2 d-1"
        }, {
            "id": "maintenance-respiration",
            "metricName": "maintenance-respiration",
            "scale": 1000.0,
            "offset": 0.0,
            "type": "number[]",
            "description": "",
            "unit": "kgC m-2 d-1"
        }, {
            "id": "growth-respiration",
            "metricName": "growth-respiration",
            "scale": 1000.0,
            "offset": 0.0,
            "type": "number[]",
            "description": "",
            "unit": "kgC m-2 d-1"
        }, {
            "id": "heterotrophic-respiration",
            "type": "",
            "description": "",
            "scale": 1000.0,
            "offset": 0.0,
            "unit": "kgC m-2 d-1",
            "metricName": "heterotrophic-respiration"
        }, {
            "id": "daily-total-litter-fall",
            "metricName": "daily-total-litter-fall",
            "scale": 1000.0,
            "offset": 0.0,
            "type": "number[]",
            "description": "",
            "unit": "kgC m-2 d-1"
        }, {
            "id": "daily-average-aet",
            "metricName": "daily-average-aet",
            "scale": 1000.0,
            "offset": 0.0,
            "type": "number[]",
            "description": "",
            "unit": "kgW m-2 d-1"
        }, {
            "id": "daily-average-trans",
            "type": "",
            "description": "",
            "scale": 1000.0,
            "offset": 0.0,
            "unit": "kgW m-2 d-1",
            "metricName": "daily-average-trans"
        }
    ]
    annual_cols = daily_cols
    month_cols = daily_cols
    def __init__(self, time):
        self.time = time
        self.name = 'Biome-BGC'

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

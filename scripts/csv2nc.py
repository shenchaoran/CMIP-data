import netCDF4 as nc
from os import path,chmod, remove
import stat
import sys
from math import ceil, floor
import numpy as np
import csv
import pandas as pd
import re
import linecache
import time
import matplotlib.pyplot as plt
import matplotlib
from multiprocessing import Pool
plt.switch_backend('tkagg')

SITENUM = 40595
DATA_HOME='/home/scr/Data'
COOR_PATH = DATA_HOME + '/IBIS_Data/5b9012e4c29ca433443dcfab/IBIS_site_info.txt'

GRID_LENGTH = 0.5
LON_START = -179.75
LON_END = 179.75 + GRID_LENGTH
LAT_START = -54.75
LAT_END = 82.25 + GRID_LENGTH
LAN_NUM=int((LAT_END-LAT_START)/GRID_LENGTH)
LON_NUM=int((LON_END-LON_START)/GRID_LENGTH)

YEAR_NUM = 32
TIME_START = 1982
TIME_END = TIME_START + YEAR_NUM

lons = np.arange(LON_START, LON_END, GRID_LENGTH)
lats = np.arange(LAT_START, LAT_END, GRID_LENGTH)

def readNC(ncPath, variableNames):
    dataset = nc.Dataset(ncPath, 'r+', format='NETCDF4')

    lonDimension = dataset.dimensions['long']
    latDimension = dataset.dimensions['lat']
    timeDimension = dataset.dimensions['time']

    lonVariable = dataset.variables['long']
    latVariable = dataset.variables['lat']
    timeVariable = dataset.variables['time']
    for variableName in variableNames:
        var = dataset.variables[variableName]

    # print(gppVariable.shape)
    # timeVariable.datatype = 'f4'
    # timeVariable.units = 'days since ' + str(TIME_START) + '-01-01'
    # timeVariable.calendar = '365_day'

    # lonVariable[:] = lons
    # latVariable[:] = lats
    # timeVariable[:] = [n * 365 for n in range(YEAR_NUM)]

    dataset.close()
    print('finished!')

def writeNC(argv):
    if argv['modelName'] == 'Biome-BGC':
        siteOutFolder = DATA_HOME + '/Biome_BGC_Data/5b9012e4c29ca433443dcfab/outputs'
        siteOutSuffix = '.daily.ascii'
    elif argv['modelName'] == 'IBIS':
        siteOutFolder = DATA_HOME + '/IBIS_Data/5b9012e4c29ca433443dcfab/outputs'
        siteOutSuffix = '.daily.txt'
    elif argv['modelName'] == 'LPJ':
        siteOutFolder = DATA_HOME + '/LPJ/5b9012e4c29ca433443dcfab/outputs'
        siteOutSuffix = '.daily.csv'

    if path.exists(argv['distPath']):
        remove(argv['distPath'])

    # f_log = open(argv['distPath'] + '.log', 'w')
    dataset = nc.Dataset(argv['distPath'], 'w', format='NETCDF4')

    lonDimension = dataset.createDimension('long', len(lons))
    latDimension = dataset.createDimension('lat', len(lats))
    timeDimension = dataset.createDimension('time', None)

    lonVariable = dataset.createVariable("long", 'f4', ("long"))
    latVariable = dataset.createVariable("lat", 'f4', ("lat"))
    timeVariable = dataset.createVariable("time", 'f4', ("time"))

    lonVariable.units = 'degrees_east'
    latVariable.units = 'degrees_north'
    timeVariable.units = 'days since ' + str(TIME_START) + '-01-01'
    timeVariable.calendar = '365_day'

    lonVariable[:] = lons
    latVariable[:] = lats

    if argv['average']:
        time_len = int(ceil(365/argv['step']))
    elif argv['step'] == 11680:
        time_len = 1
    else:
        time_len = int(ceil(365/argv['step'])*YEAR_NUM)
    timeVariable[:] = [n*argv['step'] for n in range(time_len)]


    vars = []
    data = []
    for i, variableName in enumerate(argv['variableNames']):
        var = dataset.createVariable(variableName, 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=4)
        # var.set_auto_mask(True)
        # var.setncattr('missing_value', 0)
        var.units = argv['units'][i]
        # print(var.units)
        data.append(np.empty([timeVariable.shape[0], LAN_NUM, LON_NUM]))
        vars.append(var)

    def parseSite(siteCfg):
        if path.exists(siteCfg['csvPath']):
            try:
                df = pd.read_csv(siteCfg['csvPath'], sep='\s+', usecols=argv['usecols'], header=None)
                for j, ndarr in enumerate(data):
                    col = np.array(df.iloc[:, j])
                    col = np.resize(col, 365*YEAR_NUM)
                    if argv['step'] == 11680:
                        ndarr[:,siteCfg['latIndex'], siteCfg['lonIndex']] = col.mean()*argv['scales'][j]
                    # elif argv['step'] == 365:
                    #     ndarr[:, siteCfg['latIndex'], siteCfg['lonIndex']] = col.reshape(YEAR_NUM, 365).mean(axis=1)*argv['scales'][j]
                    else:
                        col = col.reshape(YEAR_NUM, 365)
                        tmp = np.empty([YEAR_NUM, ceil(365/argv['step'])])
                        for k in range(YEAR_NUM):
                            tmp[k] = np.resize(col[k], ceil(365/argv['step'])*argv['step']) \
                                .reshape(-1, argv['step']) \
                                .mean(axis=1)
                        if argv['average']:
                            ndarr[:, siteCfg['latIndex'], siteCfg['lonIndex']] = tmp[:].mean(axis=0) * argv['scales'][j]
                        else:
                            ndarr[:, siteCfg['latIndex'], siteCfg['lonIndex']] = tmp[:].reshape(-1) * argv['scales'][j]
                print(i+1, SITENUM)
            except Exception as instance:
                # f_log.write(str(i+1))
                # f_log.write('\n')
                print(instance)
                print('%d null site' % (i+1))
        else:
            print('%d site doesn\'t exist' % (i+1))

    sites = []
    for i in range(SITENUM):
        siteCoorStr = linecache.getline(COOR_PATH, i+1)
        lonLat = re.split('\s+', siteCoorStr)
        siteLon = float(lonLat[0])
        siteLat = float(lonLat[1])
        lonIndex = int((siteLon - LON_START) / 0.5)
        latIndex = int((siteLat - LAT_START) / 0.5)
        if (latIndex < LAN_NUM) and (latIndex >= 0) and (lonIndex < LON_NUM) and (lonIndex >=0):
            siteOutPath = '%s/%s%s' % (siteOutFolder, str(i+1), siteOutSuffix)
            sites.append({
                'csvPath': siteOutPath,
                'lonIndex': lonIndex,
                'latIndex': latIndex
            })
        else:
            print('out of site index range: ', i+1)

    pool = Pool(processes=25)
    pool.map(parseSite, sites)

    for i, var in enumerate(vars):
        var[:] = data[i]
        if var.name == 'GPP' or var.name == 'NPP':
            # var[:] = np.ma.masked_where((var[:] <= 0.00001), var)
            var[:] = np.ma.masked_where((var[:] <= 0), var)
        # elif var.name == 'NEE' or var.name == 'NEP':
        #     var[:] = np.ma.masked_where(((var[:] == 0) | (var[:] > 8) | (var[:] < -8)), var)
    
    dataset.close()
    # f_log.close()
    print('finished!')

def maskVar(argv):
    dataset = nc.Dataset(argv['distPath'], 'r+', format='NETCDF4')
    for var in dataset.variables:
        if var.name == 'GPP' or var.name == 'NPP':
            var[:] = np.ma.masked_where((var[:] <= 0), var)
        elif var.name == 'NEE' or var.name == 'NEP':
            if var.units == 'kgC m-2 y-1':
                max = 8*.365
                min = -8*.365
            elif var.unit == 'gC m-2 d-1':
                max = 8
                min = -8
            var[:] = np.ma.masked_where((var[:] == 0), var)
    dataset.close()
    print('finished!')
        
def modifyUnit(argv):
    dataset = nc.Dataset(argv['distPath'], 'r+', format='NETCDF4')
    timeVariable = dataset.variables['time']
    for var in dataset.variables:
        # 32年平均：1个时间切片；年平均：32个时间切片；32年的月平均：12个时间切片
        if var.units == 'gC m-2 d-1' and \
            timeVariable.shape[0] <= 32 and \
            timeVariable.shape[0] != 12:
            var.units = 'kgC m-2 y-1'
            var[:] = var[:]*.365
    dataset.close()
    print('finished!')

IBIS_cols = [
    {
        "id": "adrain",
        "type": "",
        "description": "daily average rainfall rate",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "mm d-1",
        "metricName": "daily-average-rainfall-rate"
    }, {
        "id": "adsnow",
        "type": "",
        "description": "daily average snowfall rate",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "mm d-1",
        "metricName": "daily-average-snowfall-rate"
    }, {
        "id": "adaet",
        "type": "",
        "description": "daily average aet",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "mm d-1",
        "metricName": "daily-average-aet"
    }, {
        "id": "adtrans",
        "type": "",
        "description": "",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "unknown",
        "metricName": ""
    }, {
        "id": "adinvap",
        "type": "",
        "description": "",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "unknown",
        "metricName": ""
    }, {
        "id": "adsuvap",
        "type": "",
        "description": "",
        "scale": 1000.0,
        "offset": 0.0,
        "unit": "unknown",
        "metricName": ""
    }, {
        "id": "adtrunoff",
        "type": "",
        "description": "daily average total runoff",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "mm d-1",
        "metricName": "daily-average-total-runoff"
    }, {
        "id": "adsrunoff",
        "type": "",
        "description": "daily average surface runoff",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "mm d-1",
        "metricName": "daily-average-surface-runoff"
    }, {
        "id": "addrainage",
        "type": "",
        "description": "daily average drainage",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "mm d-1",
        "metricName": "daily-average-drainage"
    }, {
        "id": "adrh",
        "type": "",
        "description": "daily average relative humidity",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "percent",
        "metricName": "daily-average-rh"
    }, {
        "id": "adsnod",
        "type": "",
        "description": "daily average snow depth",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "m",
        "metricName": "daily-average-snow-depth"
    }, {
        "id": "adsnof",
        "type": "",
        "description": "daily average snow fraction",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "fraction",
        "metricName": "daily-average-snow-fraction"
    }, {
        "id": "adwsoi",
        "type": "",
        "description": "daily average soil moisture",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "fraction",
        "metricName": "daily-average-soil-moisture"
    }, {
        "id": "adwisoi",
        "type": "",
        "description": "daily average soil ice",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "fraction",
        "metricName": "daily-average-soil-ice"
    }, {
        "id": "adtsoi",
        "type": "",
        "description": "daily average soil temperature",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "°C",
        "metricName": "daily-average-soil-temperature"
    }, {
        "id": "adwsoic",
        "type": "",
        "description": "daily average soil moisture using root profile weighting",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "fraction",
        "metricName": "daily-average-soil-moisture-using-root-profile-weighting"
    }, {
        "id": "adtsoic",
        "type": "",
        "description": "daily average soil temperature using profile weighting",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "°C",
        "metricName": "daily-average-soil-temperature-using-profile-weighting"
    }, {
        "id": "adco2mic",
        "type": "",
        "description": "daily accumulated co2 respiration from microbes",
        "scale": 1000.0,
        "offset": 0.0,
        "unit": "kgN m-2 d-1",
        "metricName": "daily-accumulated-co2-respiration-from-microbes"
    }, {
        "id": "adco2root",
        "type": "",
        "description": "daily accumulated co2 respiration from roots",
        "scale": 1000.0,
        "offset": 0.0,
        "unit": "kgC m-2 d-1",
        "metricName": "daily-accumulated-co2-respiration-from-roots"
    }, {
        "id": "adco2soi",
        "type": "",
        "description": "daily accumulated co2 respiration from soil(total)",
        "scale": 1000.0,
        "offset": 0.0,
        "unit": "kgC m-2 d-1",
        "metricName": "daily-accumulated-co2-respiration-from-soil(total)"
    }, {
        "id": "adco2ratio",
        "type": "",
        "description": "ratio of root to total co2 respiration",
        "scale": 1000.0,
        "offset": 0.0,
        "unit": "kgC m-2 d-1",
        "metricName": "ratio-of-root-to-total-co2-respiration"
    }, {
        "id": "adnmintot",
        "type": "",
        "description": "daily accumulated net nitrogen mineralization",
        "scale": 1000.0,
        "offset": 0.0,
        "unit": "kgN m-2 d-1",
        "metricName": "daily-accumulated-net-nitrogen-mineralization"
    }, {
        "id": "adtlaysoi",
        "type": "",
        "description": "daily average soil temperature of top layer",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "°C",
        "metricName": "daily-average-soil-temperature-of-top-layer"
    }, {
        "id": "adwlaysoi",
        "type": "",
        "description": "daily average soil moisture of top layer",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "fraction",
        "metricName": "daily-average-soil-moisture-of-top-layer"
    }, {
        "id": "adneetot",
        "type": "",
        "description": "daily accumulated net ecosystem exchange of co2 in ecosystem",
        "scale": 1000.0,
        "offset": 0.0,
        "unit": "kgC m-2 d-1",
        "metricName": "daily-average-NEE"
    }, {
        "id": "adgpptot",
        "type": "",
        "description": "daily average GPP",
        "scale": 1000.0,
        "offset": 0.0,
        "unit": "kgC m-2 d-1",
        "metricName": "daily-average-GPP"
    }, {
        "id": "adnpptot",
        "type": "",
        "description": "daily average NPP",
        "scale": 1000.0,
        "offset": 0.0,
        "unit": "kgC m-2 d-1",
        "metricName": "daily-average-NPP"
    }
]

sys.argv[2] = int(sys.argv[2])
if sys.argv[1] in ['Biome-BGC', 'IBIS', 'LPJ'] and \
    sys.argv[2] in [1, 4, 8, 24, 32, 365, 11680]:
    if sys.argv[1] == 'Biome-BGC':
        variableNames = ['GPP']
        usecols = None
        # csv unit: kgC m-2 d-1
        units = ['gC m-2 d-1']
        scales = [1000]
    elif sys.argv[1] == 'IBIS':
        variableNames = [col['id'] for col in IBIS_cols]
        usecols = np.arange(27) + 3
        units = [col['unit'] for col in IBIS_cols]
        scales = [col['scale'] for col in IBIS_cols]
    elif sys.argv[1] == 'LPJ':
        variableNames = ['GPP']
        usecols = None
        units = ['gC m-2 d-1']               # csv 单位为 kgC m-2 d-1
        scales = [1]
    if sys.argv[2] == 365 or sys.argv[2] == 11680:          # 如果是年数据，单位使用 'kg C m-2 d-1'
        for i, unit in enumerate(units):
            if unit == 'gC m-2 d-1':
                units[i] = 'kgC m-2 y-1'
                scales[i] *= .365
                print(units[i], scales[i])
    argv = {
        'distPath': '%s-%s--.nc' % (sys.argv[2], sys.argv[1]),
        'modelName': sys.argv[1],
        'variableNames': variableNames,
        'usecols': usecols,
        'units': units,
        'scales': scales,
        'step': int(sys.argv[2]),
    }
    if(len(sys.argv) == 4 and sys.argv[3] == 'average'):
        argv['average'] = True
        argv['distPath'] = '%s-avg-%s.nc' % (sys.argv[2], sys.argv[1])
    else:
        argv['average'] = False
    argv['distPath'] = 'data/' + argv['distPath']
    writeNC(argv)
    # maskVar(argv)
    # modifyUnit(argv)
else:
    print('      invalid input argv, argv[1]=<model name> argv[2]=<step> argv[3]=average')
    print('      available model name: [\'Biome-BGC\', \'IBIS\', \'LPJ\']')
    print('      available step: [24, 32, 365, 11680]')


# sys.argv[2] = int(sys.argv[2])
# if sys.argv[1] in ['Biome-BGC', 'IBIS', 'LPJ'] and \
#     sys.argv[2] in [1, 4, 8, 24, 32, 365, 11680]:
#     if sys.argv[1] == 'Biome-BGC':
#         variableNames = ['GPP', 'NPP', 'NEP', 'NEE']
#         usecols = None
#         # csv unit: kgC m-2 d-1
#         units = ['gC m-2 d-1', 'gC m-2 d-1', 'gC m-2 d-1', 'gC m-2 d-1']
#         scales = [1000, 1000, 1000, 1000]
#     elif sys.argv[1] == 'IBIS':
#         variableNames = ['GPP', 'NPP', 'NEE']
#         usecols = [3, 4, 5]
#         units = ['gC m-2 d-1', 'gC m-2 d-1', 'gC m-2 d-1']               # csv 单位为 kgC m-2 d-1
#         scales = [1, 1, 1]
#     elif sys.argv[1] == 'LPJ':
#         variableNames = ['GPP', 'NPP']
#         usecols = None
#         units = ['gC m-2 d-1', 'gC m-2 d-1']               # csv 单位为 kgC m-2 d-1
#         scales = [1, 1]
#     if sys.argv[2] == 365 or sys.argv[2] == 11680:          # 如果是年数据，单位使用 'kg C m-2 d-1'
#         for i, unit in enumerate(units):
#             if unit == 'gC m-2 d-1':
#                 unit = 'kgC m-2 y-1'
#                 scales[i] *= .365
#     argv = {
#         'distPath': '%s-%s.nc' % (sys.argv[2], sys.argv[1]),
#         'modelName': sys.argv[1],
#         'variableNames': variableNames,
#         'usecols': usecols,
#         'units': units,
#         'scales': scales,
#         'step': int(sys.argv[2]),
#     }
#     if(len(sys.argv) == 4 and sys.argv[3] == 'average'):
#         argv['average'] = True
#         argv['distPath'] = '%s-avg-%s.nc' % (sys.argv[2], sys.argv[1])
#     else:
#         argv['average'] = False
#     argv['distPath'] = 'data/' + argv['distPath']
#     writeNC(argv)
#     # maskVar(argv)
#     # modifyUnit(argv)
# else:
#     print('      invalid input argv, argv[1]=<model name> argv[2]=<step> argv[3]=average')
#     print('      available model name: [\'Biome-BGC\', \'IBIS\', \'LPJ\']')
#     print('      available step: [24, 32, 365, 11680]')
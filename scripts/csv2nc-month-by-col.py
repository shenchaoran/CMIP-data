import netCDF4 as nc
from os import path, chmod, remove, mkdir
import sys, getopt, stat
from math import ceil, floor
import numpy as np
import csv
import pandas as pd
import re
import linecache
import time
import matplotlib.pyplot as plt
import matplotlib
from multiprocessing import Pool, sharedctypes, RawArray, RawValue
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

LONS = np.arange(LON_START, LON_END, GRID_LENGTH)
LATS = np.arange(LAT_START, LAT_END, GRID_LENGTH)

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

    # lonVariable[:] = LONS
    # latVariable[:] = LATS
    # timeVariable[:] = [n * 365 for n in range(YEAR_NUM)]

    dataset.close()
    print('finished!')

def parseSite(site):
    if path.exists(site['csvPath']):
        try:
            counter.value += 1
            print('counter: %s    %5.2f%%    site index: %s' % (str(counter.value), \
                counter.value*100/SITENUM, str(site['i'])))
            df = pd.read_csv(site['csvPath'], sep='\s+', usecols=site['usecols'], header=None)
            col = np.array(df.iloc[:, 0])
            # X_np (time, lat, lon)
            # col (time)
            if site['average']:
                X_np[:, site['latIndex'], site['lonIndex']] = col[:].reshape(YEAR_NUM, 12).mean(axis=0)
            else:
                X_np[:, site['latIndex'], site['lonIndex']] = col[:]
        except Exception as instance:
            # f_log.write(str(i+1))
            # f_log.write('\n')
            print(instance)
            print('%d null site' % (site['i']+1))
    else:
        print('%d site doesn\'t exist' % (i+1))

def writeNC(argv):
    if argv['modelName'] == 'Biome-BGC':
        siteOutFolder = DATA_HOME + '/Biome_BGC_Data/5b9012e4c29ca433443dcfab/outputs'
        siteOutSuffix = '.daily.ascii'
    elif argv['modelName'] == 'IBIS':
        siteOutFolder = DATA_HOME + '/IBIS_Data/5b9012e4c29ca433443dcfab/outputs'
        siteOutSuffix = '.month.txt'
    elif argv['modelName'] == 'LPJ':
        siteOutFolder = DATA_HOME + '/LPJ/5b9012e4c29ca433443dcfab/outputs'
        siteOutSuffix = '.daily.csv'

    if path.exists(argv['distPath']):
        remove(argv['distPath'])

    # f_log = open(argv['distPath'] + '.log', 'w')
    dataset = nc.Dataset(argv['distPath'], 'w', format='NETCDF4')

    lonDimension = dataset.createDimension('long', len(LONS))
    latDimension = dataset.createDimension('lat', len(LATS))
    timeDimension = dataset.createDimension('time', None)

    lonVariable = dataset.createVariable("long", 'f4', ("long"))
    latVariable = dataset.createVariable("lat", 'f4', ("lat"))
    timeVariable = dataset.createVariable("time", 'f4', ("time"))

    lonVariable.units = 'degrees_east'
    latVariable.units = 'degrees_north'
    timeVariable.units = 'days since ' + str(TIME_START) + '-01-01'
    timeVariable.calendar = '365_day'

    lonVariable[:] = LONS
    latVariable[:] = LATS

    if argv['average']:
        time_len = 12
    else:
        time_len = 12*YEAR_NUM
    timeVariable[:] = [n*30 for n in range(time_len)]


    var = dataset.createVariable(argv['variableName'], 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=4)
    var.units = argv['unit']

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
            site = {
                'csvPath': siteOutPath,
                'lonIndex': lonIndex,
                'latIndex': latIndex,
                'usecols': argv['usecols'],
                'average': argv['average'],
                'i': i,
            }
            sites.append(site)
            if not multiprocessing:
                parseSite(site)
        else:
            print('out of site index range: ', i+1)
    if multiprocessing:
        pool = Pool(processes=30)
        pool.map(parseSite, sites)
        pool.close()
        pool.join()
    var[:] = X_np
    if var.name == 'GPP' or var.name == 'NPP':
        # var[:] = np.ma.masked_where((var[:] <= 0.00001), var)
        var[:] = np.ma.masked_where(np.less_equal(var[:], 0), var)
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

counter = RawValue('i')
counter.value = 0
average = False
multiprocessing = True
step = 1
options, args = getopt.getopt(sys.argv[1:], '', ['model=', 'var=', 'step=', 'average=', 'multiprocessing='])
for opt in options:
    if(opt[0] == '--model'):
        model = opt[1]
    elif(opt[0] == '--var'):
        var = opt[1]
    elif(opt[0] == '--step'):
        step = int(opt[1])
    elif(opt[0] == '--average'):
        if opt[1] in ['true', 'True', '1', 't', 'y']:
            average = True
    elif(opt[0] == '--multiprocessing'):
        if(opt[1] in ['False', 'false', '0', 'f', 'F', 'n', 'N']):
            multiprocessing = False

if average:
    time_len = 12
else:
    time_len = YEAR_NUM * 12
X_shape = (time_len, LAN_NUM, LON_NUM)
X = RawArray('d', time_len * LAN_NUM * LON_NUM)
X_np = np.frombuffer(X).reshape(X_shape)

distFolder = './data/%s-month' % (model)
if(average):
    distFolder = '%s-avg' % (distFolder)
if not path.exists(distFolder):
    mkdir(distFolder)

if model in ['Biome-BGC', 'IBIS', 'LPJ'] and step in [1, 12, time_len]:
    if model == 'Biome-BGC':
        cols = []
    elif model == 'IBIS':
        cols = [
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
    elif model == 'LPJ':
        cols = []
    

    for i, col in enumerate(cols):
        if(col['id'] == var):
            selectedCol = col
            selectedIndex = i
    if 'selectedCol' in locals():
        argv = {
            'distPath': '%s/%s.nc' % (distFolder, selectedCol['id']),
            'modelName': model,
            'variableName': selectedCol['id'],
            'usecols': [selectedIndex + 1],
            'unit': selectedCol['unit'],
            'scale': selectedCol['scale'],
            'step': step,
        }
        if step == 365 or step == 11680:          # 如果是年数据，单位使用 'kg C m-2 d-1'
            if argv['unit'] == 'gC m-2 d-1':
                argv['unit'] = 'kgC m-2 y-1'
                argv['scale'] *= .365
        if(len(sys.argv) == 4 and sys.argv[3] == 'average'):
            argv['average'] = True
        else:
            argv['average'] = False
        writeNC(argv)
        # maskVar(argv)
        # modifyUnit(argv)
    else:
        print('      variable doesn\'t exist')
else:
    print('      invalid input argv, argv[1]=<model name> argv[2]=<step> argv[3]=average')
    print('      available model name: [\'Biome-BGC\', \'IBIS\', \'LPJ\']')
    print('      available step: [24, 32, 365, 11680]')
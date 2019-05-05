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

def parseSite(siteCfg):
    if path.exists(siteCfg['csvPath']):
        try:
            df = pd.read_csv(siteCfg['csvPath'], sep='\s+', usecols=argv['usecols'], header=None)
            col = np.array(df.iloc[:, 0])
            col = np.resize(col, 365*YEAR_NUM)
            # X_np = np.ctypeslib.as_array(shared_array)
            if argv['step'] == 11680:
                X_np[:,siteCfg['latIndex'], siteCfg['lonIndex']] = col.mean()*argv['scale']
            else:
                col = col.reshape(YEAR_NUM, 365)
                tmp = np.empty([YEAR_NUM, ceil(365/argv['step'])])
                for k in range(YEAR_NUM):
                    tmp[k] = np.resize(col[k], ceil(365/argv['step'])*argv['step']) \
                        .reshape(-1, argv['step']) \
                        .mean(axis=1)
                if argv['average']:
                    X_np[:, siteCfg['latIndex'], siteCfg['lonIndex']] = tmp[:].mean(axis=0) * argv['scale']
                else:
                    X_np[:, siteCfg['latIndex'], siteCfg['lonIndex']] = tmp[:].reshape(-1) * argv['scale']
            counter.value += 1
            print('counter: %s    %5.2f%%    site index: %s' % (counter.value, \
                counter.value*100/SITENUM, \
                siteCfg['i']))
        except Exception as instance:
            # f_log.write(str(i+1))
            # f_log.write('\n')
            print(instance)
            print('%d null site' % (siteCfg['i']+1))
    else:
        print('%d site doesn\'t exist' % (i+1))

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
        time_len = int(ceil(365/argv['step']))
    elif argv['step'] == 11680:
        time_len = 1
    else:
        time_len = int(ceil(365/argv['step'])*YEAR_NUM)
    timeVariable[:] = [n*argv['step'] for n in range(time_len)]


    var = dataset.createVariable(argv['variableName'], 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=4)
    var.units = argv['unit']
    # ndarr = np.empty([timeVariable.shape[0], LAN_NUM, LON_NUM])
    # ndarr = np.ctypeslib.as_ctypes(np.zeros((timeVariable.shape[0], LAN_NUM, LON_NUM)))
    # shared_array = sharedctypes.RawArray(ndarr._type_, ndarr)

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

counter = RawValue('i')
counter.value = 0
average = False
multiprocessing = True
options, args = getopt.getopt(sys.argv[1:], '', ['model=', 'var=', 'step=', 'average=', 'multiprocessing='])
for opt in options:
    if(opt[0] == '--model'):
        model = opt[1]
    elif(opt[0] == '--var'):
        var = opt[1]
    elif(opt[0] == '--step'):
        step = int(opt[1])
    elif(opt[0] == '--average'):
        # average = opt[1] in ['true', 'True', '1', 't', 'y']
        average = True
    elif(opt[0] == '--multiprocessing'):
        if(opt[1] in ['False', 'false', '0', 'f', 'F', 'n', 'N']):
            multiprocessing = False

if average:
    time_len = int(ceil(365/step))
elif step == 11680:
    time_len = 1
else:
    time_len = int(ceil(365/step) * YEAR_NUM)
X_shape = (time_len, LAN_NUM, LON_NUM)
X = RawArray('d', time_len * LAN_NUM * LON_NUM)
X_np = np.frombuffer(X).reshape(X_shape)

distFolder = './data/%s-%s' % (model, step)
if(average):
    distFolder = '%s-avg' % (distFolder)
if not path.exists(distFolder):
    mkdir(distFolder)

if model in ['Biome-BGC', 'IBIS', 'LPJ'] and step in [8, 32, 365, 11680]:
    if model == 'Biome-BGC':
        cols = []
    elif model == 'IBIS':
        cols = 
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
            'usecols': [selectedIndex + 1] + 3, # 跳過年月日三列
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
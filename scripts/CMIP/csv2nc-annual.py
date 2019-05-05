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
from MS.IBIS import *
from MS.LPJ import *
from MS.Biome_BGC import *
from CMIP import *

def parseSite(site):
    counter.value += 1
    if path.exists(site['csvPath']):
        print('counter: %s    %5.2f%%    site index: %s' % (str(counter.value), \
            counter.value*100/SITENUM, str(site['i'])))
        try:
            # X_np: (var, time, lat, lon)
            # cols: (time, var)
            df = pd.read_csv(site['csvPath'], sep='\s+', usecols=usecols, header=None)
            df = df.replace(to_replace='\*+', value='0', regex=True)
            for i, column in enumerate(df.columns):
                df[[column]] = df[[column]].astype('float64')
            if average:
                X_np[:, 0, site['latIndex'], site['lonIndex']] = df[:].transpose().mean(axis=0)
            else:
                X_np[:, :, site['latIndex'], site['lonIndex']] = df[:].transpose()
        except Exception as instance:
            # f_log.write(str(i+1))
            # f_log.write('\n')
            print(instance)
            print('%d null site' % (site['i']+1))
    else:
        print(site['csvPath'])
        print('%d site doesn\'t exist' % (site['i']+1))

def writeNC():
    if path.exists(ncPath):
        remove(ncPath)

    # f_log = open(argv['distPath'] + '.log', 'w')
    dataset = nc.Dataset(ncPath, 'w', format='NETCDF4')

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

    if average:
        time_len = 1
    else:
        time_len = YEAR_NUM
    timeVariable[:] = [n*365 for n in range(time_len)]

    vars = []
    for i, variableName in enumerate(variableNames):
        var = dataset.createVariable(variableName, 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=4)
        var.units = units[i]
        vars.append(var)

    sites = []
    for i in range(SITENUM):
        siteCoorStr = linecache.getline(COOR_PATH, i+1)
        lonLat = re.split('\s+', siteCoorStr)
        siteLon = float(lonLat[0])
        siteLat = float(lonLat[1])
        lonIndex = int((siteLon - LON_START) / 0.5)
        latIndex = int((siteLat - LAT_START) / 0.5)
        if (latIndex < LAT_NUM) and (latIndex >= 0) and (lonIndex < LON_NUM) and (lonIndex >=0):
            siteOutPath = '%s/%s%s' % (ms.folder, str(i+1), ms.suffix)
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
    
    for i, var in enumerate(vars):
        tmp = X_np[i] * scales[i]
        if var.name == 'aygpptot' or var.name == 'ayanpptot' or var.name == 'aynpptot':
            # var[:] = np.ma.masked_where((var[:] <= 0.00001), var)
            masked = np.ma.masked_less(tmp, 0)
            # elif var.name == 'NEE' or var.name == 'NEP':
            #     var[:] = np.ma.masked_where(((var[:] == 0) | (var[:] > 8) | (var[:] < -8)), var)
        else:
            # masked = np.ma.masked_equal(tmp, 0)
            masked = tmp
        var[:] = masked
    
    dataset.close()
    # f_log.close()
    print('finished!')

ibis = IBIS('original-annual')
ibis_lishihua = IBIS('lishihua')
biome_bgc = Biome_BGC('original-annual')
lpj = LPJ('original-annual')
counter = RawValue('i')
counter.value = 0
step = 1
average = False
multiprocessing = True
options, args = getopt.getopt(sys.argv[1:], '', ['model='])
for opt in options:
    if(opt[0] == '--model'):
        if opt[1] == 'IBIS':
            ms = ibis
        elif opt[1] == 'Biome-BGC':
            ms = biome_bgc
        elif opt[1] == 'LPJ':
            ms = lpj
        elif opt[1] =='IBIS-lishihua':
            ms = ibis_lishihua

if average:
    time_len = 1
else:
    time_len = YEAR_NUM

distFolder = '../data/original-annual'
if not path.exists(distFolder):
    mkdir(distFolder)

if ms.name in ['Biome-BGC', 'IBIS', 'IBIS-lishihua', 'LPJ'] and step in [1, 32]:
    X_shape = (len(ms.cols), time_len, LAT_NUM, LON_NUM)
    X = RawArray('d', len(ms.cols) * time_len * LAT_NUM * LON_NUM)
    X_np = np.frombuffer(X).reshape(X_shape)

    ncPath = '%s/%s.nc' % (distFolder, ms.name)
    if(average):
        ncPath = '%s/%s-avg.nc' % (distFolder, ms.name)
    variableNames = [col.get('id') for col in ms.cols]
    usecols = np.arange(len(ms.cols))
    scales = [col.get('scale') if col.get('scale') else 1 for col in ms.cols]
    units = []
    for col in ms.cols:
        unit = col.get('unit')
        if unit:
            pass
        else:
            unit = ''
        units.append(unit)
    
    t1 = time.time()
    writeNC()
    t2 = time.time()
    print('执行时间：%s' % int(t2-t1))
else:
    print('      invalid input argv, argv[1]=<model name> argv[2]=<step> argv[3]=average')
    print('      available model name: [\'Biome-BGC\', \'IBIS\', \'LPJ\']')
    print('      available step: [24, 32, 365, 11680]')
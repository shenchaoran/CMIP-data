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
from MS.IBIS import *
from MS.LPJ import *
from MS.Biome_BGC import *
from CMIP import *
plt.switch_backend('tkagg')

def parseSite(site):
    counter.value += 1
    if path.exists(site['csvPath']):
        # try:
        print('counter: %s    %5.2f%%    site index: %s' % (str(counter.value), \
            counter.value*100/SITENUM, str(site['i'])))
        # X_np: (var, time, lat, lon)
        # cols: (time, var)
        df = pd.read_csv(site['csvPath'], sep='\s+', usecols=usecols, header=None)
        if average:
            X_np[:, 0, site['latIndex'], site['lonIndex']] = df[:].transpose().mean(axis=0)
        else:
            X_np[:, :, site['latIndex'], site['lonIndex']] = df[:].transpose()
        # except Exception as instance:
        #     # f_log.write(str(i+1))
        #     # f_log.write('\n')
        #     print(instance)
        #     print('%d null site' % (site['i']+1))
    else:
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
        time_len = YEAR_NUM * 12
    timeVariable[:] = [n*30 for n in range(time_len)]

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
    
    t5 = time.time()
    for i, var in enumerate(vars):
        tmp = X_np[i] * scales[i]
        if var.name == 'adgpptot' or var.name == 'adnpptot':
            masked = np.ma.masked_less(tmp, 0)
        else:
            # masked = np.ma.masked_equal(tmp, 0)
            masked = tmp
        var[:] = masked
    
    dataset.close()
    # f_log.close()
    t6 = time.time()
    
    duration3 = int(t6-t5)
    unit3 = 's'
    if duration3 > 60:
        duration3 /= 60
        unit3 = 'min'
    if duration3 > 60:
        duration3 /= 60
        unit3 = 'hour'
    print('finished!')
    print('%9s %4.2f %s' % ('写文件时间：', duration3, unit3))

ibis = IBIS('month')
biome_bgc = Biome_BGC('month')
lpj = LPJ('month')

counter = RawValue('i')
counter.value = 0
average = False
multiprocessing = True
options, args = getopt.getopt(sys.argv[1:], '', ['model=', 'average=', 'multiprocessing='])
for opt in options:
    if(opt[0] == '--model'):
        if opt[1] == 'IBIS':
            ms = ibis
        elif opt[1] == 'Biome-BGC':
            ms = biome_bgc
        elif opt[1] == 'LPJ':
            ms = lpj
    elif(opt[0] == '--average'):
        if opt[1] in ['true', 'True', '1', 't', 'y']:
            average = True
    elif(opt[0] == '--multiprocessing'):
        if opt[1] in ['False', 'false', '0', 'f', 'F', 'n', 'N']:
            multiprocessing = False

if average:
    time_len = 1
else:
    time_len = YEAR_NUM * 12

distFolder = '../data/month'
if not path.exists(distFolder):
    mkdir(distFolder)

if ms.name in ['Biome-BGC', 'IBIS', 'LPJ']:
    t1 = time.time()
    X_shape = (len(ms.cols), time_len, LAT_NUM, LON_NUM)
    size = len(ms.cols) * time_len * LAT_NUM * LON_NUM
    print('shared memory size: %4.2f GB' % (size*4/8/1024/1024/1024))
    X = RawArray('d', size)
    X_np = np.frombuffer(X).reshape(X_shape)

    t2 = time.time()
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
            if col.get('scale') == 1000:
                if unit == 'kgN m-2 d-1':
                    unit = 'gN m-2 d-1'
                elif unit == 'kgC m-2 d-1':
                    unit = 'gC m-2 d-1'
        else:
            unit = ''
        units.append(unit)

    t3 = time.time()
    writeNC()
    t4 = time.time()

    duration1 = int(t2-t1)
    duration2 = int(t4-t3)
    unit1 = 's'
    unit2 = 's'
    if duration1 > 60:
        duration1 /= 60
        unit1 = 'min'
    if duration2 > 60:
        duration2 /= 60
        unit2 = 'min'
    if duration2 > 60:
        duration2 /= 60
        unit2 = 'hour'
    print('%9s %4.2f %s' % ('分配内存时间：', duration1, unit1))
    print('%9s %4.2f %s' % ('计算时间：', duration2, unit2))
else:
    print('      invalid input argv, argv[1]=<model name> argv[3]=average')
    print('      available model name: [\'Biome-BGC\', \'IBIS\', \'LPJ\']')
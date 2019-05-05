# 将月步长的数据转为年步长和年平均值
import netCDF4 as nc
from os import path,chmod, remove
import stat
import numpy as np
import csv
import pandas
import re
import linecache
import time
from CMIP import *
from multiprocessing import Pool, sharedctypes, RawArray, RawValue

def annualAvg(cfg):
    fname = cfg['fname']
    average = cfg['average']
    srcPath = srcFolder + fname
    if average:
        distPath = distFolder + re.split('.nc', fname)[0] + '-avg.nc'
    else:
        distPath = distFolder + fname
    if path.exists(distPath):
        remove(distPath)
    srcDataset = nc.Dataset(srcPath, 'r', format='NETCDF4')
    distDataset = nc.Dataset(distPath, 'w', format='NETCDF4')

    distDataset.createDimension('long', LON_NUM)
    distDataset.createDimension('lat', LAT_NUM)
    lonVariable = distDataset.createVariable("long", 'f4', ("long"))
    latVariable = distDataset.createVariable("lat", 'f4', ("lat"))
    lonVariable.units = 'degrees_east'
    latVariable.units = 'degrees_north'
    lonVariable[:] = LONS
    latVariable[:] = LATS

    if not average:
        distDataset.createDimension('time', None)
        timeVariable = distDataset.createVariable("time", 'f4', ("time"))
        timeVariable.units = 'days since %s-01-01' % str(TIME_START)
        timeVariable.calendar = '365_day'
        timeVariable = [n*365 for n in range(TIME_START)]

    variableData = []
    for i, srcVar in enumerate(srcDataset.variables.values()):
        if srcVar.name in ['lat', 'long', 'time']:
            continue
        if average:
            var = distDataset.createVariable(srcVar.name, 'f4', ('lat', 'long'), zlib=True, least_significant_digit=4)
        else:
            var = distDataset.createVariable(srcVar.name, 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=4)
        src_unit = srcVar.units
        if src_unit in ['gC m-2 d-1', 'gN m-2 d-1', 'gW m-2 d-1'] :
            scale = .365
            if src_unit == 'gC m-2 d-1':
                dist_unit = 'kgC m-2 y-1'
            elif src_unit == 'gN m-2 d-1':
                dist_unit = 'kgN m-2 y-1'
            elif src_unit == 'gW m-2 d-1':
                dist_unit = 'kgW m-2 y-1'
        elif src_unit in ['kgC m-2 d-1', 'kgN m-2 d-1', 'kgW m-2 d-1']:
            scale = 365
            if src_unit == 'kgC m-2 d-1':
                dist_unit = 'kgC m-2 y-1'
            elif src_unit == 'kgN m-2 d-1':
                dist_unit = 'kgN m-2 y-1'
            elif src_unit == 'kgW m-2 d-1':
                dist_unit = 'kgW m-2 y-1'
        else:
            scale = 1
            dist_unit = src_unit
        var.units = dist_unit

        if average:
            tmp = srcVar[:].mean(axis=0)*scale
        else:
            tmp = srcVar[:].reshape(-1, 12, LAT_NUM, LON_NUM).mean(axis=1)*scale
        # var[:] = np.ma.masked_equal(tmp, 0)
        var[:] = tmp
    
    srcDataset.close()
    distDataset.close()
    print('%s finished!' % distPath)

# srcFolder = '/home/scr/Data/scripts/data/month/'
# distFolder = '/home/scr/Data/scripts/data/annual/'
# fnames = [
#     'Biome-BGC.nc',
#     'IBIS.nc',
#     'LPJ.nc',
# ]

# tasks = []
# for i in range(len(fnames)):
#     tasks.append({
#         "fname": fnames[i],
#         "average": False            # month -> year series data
#     })
#     tasks.append({
#         "fname": fnames[i],
#         "average": True             # month -> average yearly data
#     })

srcFolder = '/home/scr/Data/scripts/data/original-annual/'
distFolder = '/home/scr/Data/scripts/data/original-annual/'
fnames = ['IBIS-lishihua.nc']
tasks = [
    {
        "fname": fnames[0],
        "average": True
    }
]

pool = Pool(processes=30)
pool.map(annualAvg, tasks)
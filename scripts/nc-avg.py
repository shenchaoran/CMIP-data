import netCDF4 as nc
from os import path,chmod, remove
import stat
import numpy as np
import csv
import pandas
import re
import linecache
import time

SITENUM = 40595

GRID_LENGTH = 0.5
LON_START = -179.75
LON_END = 179.75 + GRID_LENGTH
LAT_START = -54.75
LAT_END = 82.25 + GRID_LENGTH

YEAR_NUM = 32
TIME_START = 1982
TIME_END = TIME_START + YEAR_NUM

LONS = np.arange(LON_START, LON_END, GRID_LENGTH)
LATS = np.arange(LAT_START, LAT_END, GRID_LENGTH)
LAT_NUM=int((LAT_END-LAT_START)/GRID_LENGTH)
LON_NUM=int((LON_END-LON_START)/GRID_LENGTH)

folder = '/home/scr/Data/scripts/data/'
# def statByLat():

# [1982, 2013]
# [2000, 2013] 年平均值
def annualAvg(srcFname, distFname, variableNames, yearIndex, scales):
    srcPath = folder + srcFname
    distPath = folder + distFname
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

    variableData = []
    for i, variableName in enumerate(variableNames):
        vari = distDataset.createVariable(variableName, 'f4', ('lat', 'long'), zlib=True, least_significant_digit=4)
        vari.set_auto_mask(True)
        vari.units = 'kgC m-2 y-1'
        meaned = srcDataset.variables[variableName][yearIndex[0]:yearIndex[1]] \
            .reshape(14*yearIndex[2], LAT_NUM, LON_NUM) \
            .mean(axis=0)*scales[i]
        vari[:] = meaned.reshape(LAT_NUM,LON_NUM)
        # vari[:] = np.ma.masked_where((vari[:] == 0), vari)
    
    srcDataset.close()
    distDataset.close()
    print('finished!')

srcFnames = [
    '365-Biome-BGC.nc',
    '365-IBIS.nc',
    '365-LPJ.nc',
    '8-MOD17A2.nc'
]
distFnames = [
    '2000-2013-avg-Biome-BGC.nc',
    '2000-2013-avg-IBIS.nc',
    '2000-2013-avg-LPJ.nc',
    '2000-2013-avg-MOD17A2.nc'
]
variableNames = [
    ['GPP'],
    ['GPP'],
    ['GPP'],
    ['GPP']
]
scales = [
    [1],
    [1],
    [1],
    [.365]
]
# variableNames = [
#     ['GPP', 'NPP', 'NEP', 'NEE'],
#     ['GPP', 'NPP', 'NEE'],
#     ['GPP', 'NPP'],
#     ['GPP']
# ]
# scales = [
#     [.365, .365, .365, .365],
#     # [.001/2.5, .001/2.5, .001/2.5],
#     [.365, .365, .365],
#     [.365, .365],
#     [.365]
# ]
yearIndexs = [
    [18, 32, 1],
    [18, 32, 1],
    [18, 32, 1],
    [0, 644, 46]
]

for i in range(len(srcFnames)):
    annualAvg(srcFnames[i], distFnames[i], variableNames[i], yearIndexs[i], scales[i])

# i=0
# annualAvg(srcFnames[i], distFnames[i], variableNames[i], yearIndexs[i], scales[i])
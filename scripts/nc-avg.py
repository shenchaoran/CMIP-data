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
DATA_HOME='/home/scr/Data'
COOR_PATH = DATA_HOME + '/IBIS_Data/5b9012e4c29ca433443dcfab/IBIS_site_info.txt'

BIOME_OUT_PATH = DATA_HOME + '/Biome_BGC_Data/5b9012e4c29ca433443dcfab/outputs'
BIOME_OUT_SUFFIX = '.annual-avg.ascii'
BIOME_NC_PATH = 'Biome-BGC-annual-output.nc'

IBIS_OUT_PATH = DATA_HOME + '/IBIS_Data/5b9012e4c29ca433443dcfab/outputs'
IBIS_OUT_SUFFIX = '.annual.txt'
IBIS_NC_PATH = 'IBIS-annual-out.nc'

GRID_LENGTH = 0.5
LON_START = -179.75
LON_END = 179.75 + GRID_LENGTH
LAT_START = -54.75
LAT_END = 82.25 + GRID_LENGTH

TIME_SPAN = 32
TIME_START = 1982
TIME_END = TIME_START + TIME_SPAN

lons = np.arange(LON_START, LON_END, GRID_LENGTH)
lats = np.arange(LAT_START, LAT_END, GRID_LENGTH)
latNum=int((LAT_END-LAT_START)/GRID_LENGTH)
lonNum=int((LON_END-LON_START)/GRID_LENGTH)

folder = '/home/scr/Data/scripts/data/'

def readNC():
    srcDataset = nc.Dataset(BIOME_NC_PATH, 'r+', format='NETCDF4')

    lonDimension = srcDataset.dimensions['long']
    latDimension = srcDataset.dimensions['lat']
    timeDimension = srcDataset.dimensions['time']

    lonVariable = srcDataset.variables['long']
    latVariable = srcDataset.variables['lat']
    timeVariable = srcDataset.variables['time']
    gppVariable = srcDataset.variables['GPP']
    nppVariable = srcDataset.variables['NPP']
    nepVariable = srcDataset.variables['NEP']
    neeVariable = srcDataset.variables['NEE']

    print(gppVariable.shape)

    srcDataset.close()
    print('finished!')

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

    distDataset.createDimension('long', lonNum)
    distDataset.createDimension('lat', latNum)
    lonVariable = distDataset.createVariable("long", 'f4', ("long"))
    latVariable = distDataset.createVariable("lat", 'f4', ("lat"))
    lonVariable.units = 'degrees_east'
    latVariable.units = 'degrees_north'
    lonVariable[:] = lons
    latVariable[:] = lats

    variableData = []
    for i, variableName in enumerate(variableNames):
        vari = distDataset.createVariable(variableName, 'f4', ('lat', 'long'), zlib=True, least_significant_digit=4)
        vari.set_auto_mask(True)
        vari.units = 'kgC m-2 y-1'
        meaned = srcDataset.variables[variableName][yearIndex[0]:yearIndex[1]] \
            .reshape(14*yearIndex[2], latNum, lonNum) \
            .mean(axis=0)*scales[i]
        vari[:] = meaned.reshape(latNum,lonNum)
        vari[:] = np.ma.masked_where((vari[:] == 0), vari)
    
    srcDataset.close()
    distDataset.close()
    print('finished!')

srcFnames = [
    'Biome-BGC-annual-out.nc',
    'IBIS-annual-out.nc',
    'LPJ-annual-out.nc',
    'MOD17A2-GPP.nc'
]
distFnames = [
    'Biome-BGC-2000-2013-avg.nc',
    'IBIS-2000-2013-avg.nc',
    'LPJ-2000-2013-avg.nc',
    'MOD17A2-2000-2013-avg.nc'
]
variableNames = [
    ['GPP', 'NPP', 'NEP', 'NEE'],
    ['GPP', 'NPP', 'NEE'],
    ['GPP', 'NPP'],
    ['GPP']
]
scales = [
    [.001, .001, .001, .001],
    [.001/2.5, .001/2.5, .001/2.5],
    [.001, .001],
    [.365]
]
yearIndexs = [
    [18, 32, 1],
    [18, 32, 1],
    [18, 32, 1],
    [0, 644, 46]
]

for i in range(len(srcFnames)):
    annualAvg(srcFnames[i], distFnames[i], variableNames[i], yearIndexs[i], scales[i])

# annualAvg(srcFnames[3], distFnames[3], variableNames[3])
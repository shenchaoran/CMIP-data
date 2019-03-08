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
BIOME_NC_PATH = 'data/Biome-BGC-annual-out.nc'
BIOME_ERR_PATH = 'data/Biome-BGC-error.log'

IBIS_OUT_PATH = DATA_HOME + '/IBIS_Data/5b9012e4c29ca433443dcfab/outputs'
IBIS_OUT_SUFFIX = '.annual.txt'
IBIS_NC_PATH = 'data/IBIS-annual-out.nc'
IBIS_ERR_PATH = 'data/IBIS-error.log'

GRID_LENGTH = 0.5
LON_START = -179.75
LON_END = 179.75 + GRID_LENGTH
LAT_START = -54.75
LAT_END = 82.25 + GRID_LENGTH
LAT_COUNT = (LAT_END-LAT_START)/GRID_LENGTH
LON_COUNT = (LON_END-LON_START)/GRID_LENGTH

TIME_SPAN = 32
TIME_START = 1982
TIME_END = TIME_START + TIME_SPAN

lons = np.arange(LON_START, LON_END, GRID_LENGTH)
lats = np.arange(LAT_START, LAT_END, GRID_LENGTH)

lanNum=int((LAT_END-LAT_START)/GRID_LENGTH)
lonNum=int((LON_END-LON_START)/GRID_LENGTH)
logFile = open(IBIS_ERR_PATH, 'w')
arr = []
for i in range(SITENUM):
    siteCoorStr = linecache.getline(COOR_PATH, i+1)
    lonLat = re.split('\s+', siteCoorStr)
    siteLon = float(lonLat[0])
    siteLat = float(lonLat[1])
    lonIndex = int((siteLon - LON_START) / 0.5)
    latIndex = int((siteLat - LAT_START) / 0.5)
    filepath = IBIS_OUT_PATH + '/' + str(i+1) + IBIS_OUT_SUFFIX
    # tmp = str(lonIndex) + '-' + str(latIndex)
    # if tmp in arr:
    #     print(i+1, '\t', siteCoorStr, '\t exits')
    # else:
    #     arr.append(tmp)
    # if (latIndex >= LAT_COUNT) or (latIndex < 0) and (lonIndex >= LON_COUNT) and(lonIndex < 0):
    #     print(i+1, '\t', siteCoorStr, '\t exits')
    
print('finished!')


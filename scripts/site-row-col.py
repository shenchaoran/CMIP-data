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

IBIS_OUT_PATH = DATA_HOME + '/IBIS_Data/5b9012e4c29ca433443dcfab/lishihua/Output/correct'
IBIS_OUT_SUFFIX = '.txt'
IBIS_NC_PATH = 'data/lishihua-ann-IBIS.nc'
IBIS_ERR_PATH = 'data/IBIS-error.log'

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


for i in range(SITENUM):
    siteCoorStr = linecache.getline(COOR_PATH, i+1)
    lonLat = re.split('\s+', siteCoorStr)
    siteLon = float(lonLat[0])
    siteLat = float(lonLat[1])
    lonIndex = int((siteLon - LON_START) / 0.5)
    latIndex = int((siteLat - LAT_START) / 0.5)
print('finished!')

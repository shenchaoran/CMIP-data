import netCDF4 as nc
from os import path
import numpy as np
import random
import csv
import pandas
import re
import linecache
import time
from datetime import datetime, timedelta
from netCDF4 import num2date, date2num, date2index

SITENUM = 40595
COOR_PATH = '/mnt/hgfs/WIN-STD-DATA/IBIS_Data/5b9012e4c29ca433443dcfab/input/IBIS_site_info.txt'

BIOME_OUT_PATH = '/mnt/hgfs/WIN-STD-DATA/Biome_BGC_Data/5b9012e4c29ca433443dcfab/outputs'
BIOME_OUT_SUFFIX = '.annual.ascii'

IBIS_OUT_PATH = '/mnt/hgfs/WIN-STD-DATA/IBIS_Data/5b9012e4c29ca433443dcfab/output'
IBIS_OUT_SUFFIX = '_IBIS_output.txt'
IBIS_NC_PATH = 'IBIS-out.nc'

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

def writeNC(outputPath):
    dataset = nc.Dataset(outputPath, 'w', format='NETCDF4')

    lonDimension = dataset.createDimension('long', len(lons))
    latDimension = dataset.createDimension('lat', len(lats))
    timeDimension = dataset.createDimension('time', TIME_SPAN)

    lonVariable = dataset.createVariable("long", 'f4', ("long"))
    latVariable = dataset.createVariable("lat", 'f4', ("lat"))
    timeVariable = dataset.createVariable("time", 'u1', ("time"))

    tempVariable = dataset.createVariable('temp', 'f8', ('time', 'lat', 'long'))

    lonDimension = dataset.dimensions['long']
    latDimension = dataset.dimensions['lat']
    timeDimension = dataset.dimensions['time']

    lonVariable = dataset.variables['long']
    latVariable = dataset.variables['lat']
    timeVariable = dataset.variables['time']
    tempVariable = dataset.variables['temp']

    lonVariable.units = 'degrees_east'
    latVariable.units = 'degrees_north'
    timeVariable.units = 'days since ' + str(TIME_START) + '-01-01'
    timeVariable.calendar = '365_day'

    lonVariable[:] = lons
    latVariable[:] = lats
    dates = [datetime(TIME_START, 1, 1) + n * timedelta(days=1) for n in range(TIME_SPAN)]
    timeVariable[:] = date2num(dates, units=timeVariable.units, calendar=timeVariable.calendar)

    tempVariable[:,:,:] = np.random.randint(0,65535, len(lons) * len(lats) * TIME_SPAN).reshape(TIME_SPAN, len(lats), len(lons))

    dataset.close()
    print('finished!')

writeNC('data/random-4d-lat-lon-time-temp.nc')
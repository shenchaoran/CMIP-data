import netCDF4 as nc
from os import path,chmod, remove
import stat
import numpy as np
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
BIOME_NC_PATH = 'data/Biome-BGC-out.nc'

IBIS_OUT_PATH = '/mnt/hgfs/WIN-STD-DATA/IBIS_Data/5b9012e4c29ca433443dcfab/output'
IBIS_OUT_SUFFIX = '_IBIS_output.txt'
IBIS_NC_PATH = 'data/IBIS-out.nc'

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

def readNC():
    dataset = nc.Dataset(IBIS_NC_PATH, 'r+', format='NETCDF4')

    lonDimension = dataset.dimensions['long']
    latDimension = dataset.dimensions['lat']
    timeDimension = dataset.dimensions['time']

    lonVariable = dataset.variables['long']
    latVariable = dataset.variables['lat']
    timeVariable = dataset.variables['time']
    falllVariable = dataset.variables['falll']
    fallwVariable = dataset.variables['fallw']
    aylailVariable = dataset.variables['aylail']
    aylaiuVariable = dataset.variables['aylaiu']
    ayco2micVariable = dataset.variables['ayco2mic']

    lonVariable.units = 'degrees_east'
    latVariable.units = 'degrees_north'
    timeVariable.units = 'days since ' + str(TIME_START) + '-01-01 00:00:00.0'
    timeVariable.calendar = '365_day'

    lonVariable[:] = lons
    latVariable[:] = lats
    dates = [datetime(TIME_START, 1, 1) + n * timedelta(days=365) for n in range(TIME_SPAN)]
    timeVariable[:] = date2num(dates, units=timeVariable.units, calendar=timeVariable.calendar)

    dataset.close()
    print('finished!')

def writeNC():
    if path.exists(IBIS_NC_PATH):
        remove(IBIS_NC_PATH)

    dataset = nc.Dataset(IBIS_NC_PATH, 'w', format='NETCDF4')

    lonDimension = dataset.createDimension('long', len(lons))
    latDimension = dataset.createDimension('lat', len(lats))
    timeDimension = dataset.createDimension('time', TIME_SPAN)

    lonVariable = dataset.createVariable("long", 'f4', ("long"))
    latVariable = dataset.createVariable("lat", 'f4', ("lat"))
    timeVariable = dataset.createVariable("time", 'f4', ("time"))

    falllVariable = dataset.createVariable('falll', 'f8', ('time', 'lat', 'long'), zlib=True, least_significant_digit=3)
    fallwVariable = dataset.createVariable('fallw', 'f8', ('time', 'lat', 'long'), zlib=True, least_significant_digit=3)
    aylailVariable = dataset.createVariable('aylail', 'f8', ('time', 'lat', 'long'), zlib=True, least_significant_digit=3)
    aylaiuVariable = dataset.createVariable('aylaiu', 'f8', ('time', 'lat', 'long'), zlib=True, least_significant_digit=3)
    ayco2micVariable = dataset.createVariable('ayco2mic', 'f8', ('time', 'lat', 'long'), zlib=True, least_significant_digit=3)

    lonVariable.units = 'degrees_east'
    latVariable.units = 'degrees_north'
    timeVariable.units = 'days since ' + str(TIME_START) + '-01-01 00:00:00.0'
    timeVariable.calendar = '365_day'

    lonVariable[:] = lons
    latVariable[:] = lats
    # dates = [datetime(TIME_START, 1, 1) + n * timedelta(days=365) for n in range(TIME_SPAN)]
    # timeVariable[:] = date2num(dates, units=timeVariable.units, calendar=timeVariable.calendar)
    timeVariable[:] = [n*365 for n in range(TIME_SPAN)]

    for i in range(SITENUM):
        siteCoorStr = linecache.getline(COOR_PATH, i+1)
        lonLat = re.split('\s+', siteCoorStr)
        siteLon = float(lonLat[0])
        siteLat = float(lonLat[1])
        lonIndex = (siteLon - LON_START) / 0.5
        latIndex = (siteLat - LAT_START) / 0.5
        filepath = IBIS_OUT_PATH + '/' + str(i+1) + IBIS_OUT_SUFFIX
        if path.exists(filepath):
            siteData = pandas.read_csv(filepath, sep='\s+', usecols=[1,2,3,4,5], header=None)
            falllVariable[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [0]])
            fallwVariable[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [1]])
            aylailVariable[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [2]])
            aylaiuVariable[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [3]])
            ayco2micVariable[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [4]])
            print(i, SITENUM)

    dataset.close()
    print('finished!')

writeNC()
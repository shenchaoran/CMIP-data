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
COOR_PATH = 'data/IBIS_site_info.txt'
INPUT_PATH = 'data/met-site'
OUTPUT_PATH = 'data'
OUTPUT_FILE_NAME = 'Biome-BGC-met.nc'
MET_PATH = INPUT_PATH
NC_PATH = OUTPUT_PATH + '/' + OUTPUT_FILE_NAME
MET_SUFFIX = '.mtc43'

GRID_LENGTH = 0.5
LON_START = -179.75
LON_END = 179.75 + GRID_LENGTH
LAT_START = -54.75
LAT_END = 82.25 + GRID_LENGTH

TIME_SPAN = 32 * 365
TIME_START = 1982
TIME_END = TIME_START + TIME_SPAN

lons = np.arange(LON_START, LON_END, GRID_LENGTH)
lats = np.arange(LAT_START, LAT_END, GRID_LENGTH)


def writeNC():
    if path.exists(NC_PATH):
        remove(NC_PATH)

    dataset = nc.Dataset(NC_PATH, 'w', format='NETCDF4')

    lonDimension = dataset.createDimension('long', len(lons))
    latDimension = dataset.createDimension('lat', len(lats))
    timeDimension = dataset.createDimension('time', None)

    lonVariable = dataset.createVariable("long", 'f4', ("long"))
    latVariable = dataset.createVariable("lat", 'f4', ("lat"))
    timeVariable = dataset.createVariable("time", 'f4', ("time"))

    tmaxVariable = dataset.createVariable('tmax', 'f4', ('time', 'lat', 'long'))
    tminVariable = dataset.createVariable('tmin', 'f4', ('time', 'lat', 'long'))
    tdayVariable = dataset.createVariable('tday', 'f4', ('time', 'lat', 'long'))
    prcpVariable = dataset.createVariable('prcp', 'f4', ('time', 'lat', 'long'))
    vpdVariable = dataset.createVariable('vpd', 'f4', ('time', 'lat', 'long'))
    sradVariable = dataset.createVariable('srad', 'f4', ('time', 'lat', 'long'))
    daylenVariable = dataset.createVariable('daylen', 'f4', ('time', 'lat', 'long'))

    lonVariable.units = 'degrees_east'
    latVariable.units = 'degrees_north'
    timeVariable.units = 'days since ' + str(TIME_START) + '-01-01'
    timeVariable.calendar = '365_day'
    tmaxVariable.units = 'deg C'
    tminVariable.units = 'deg C'
    tdayVariable.units = 'deg C'
    prcpVariable.units = 'cm'
    vpdVariable.units = 'Pa'
    sradVariable.units = 'W m-2'
    daylenVariable.units = 's'

    tmaxVariable.set_auto_mask(False)
    tminVariable.set_auto_mask(False)
    tdayVariable.set_auto_mask(False)
    prcpVariable.set_auto_mask(False)
    vpdVariable.set_auto_mask(False)
    sradVariable.set_auto_mask(False)
    daylenVariable.set_auto_mask(False)


    lonVariable[:] = lons
    latVariable[:] = lats
    timeVariable[:] = np.arange(0, TIME_SPAN, 1)

    for i in range(SITENUM):
        siteCoorStr = linecache.getline(COOR_PATH, i+1)
        lonLat = re.split('\s+', siteCoorStr)
        siteLon = float(lonLat[0])
        siteLat = float(lonLat[1])
        lonIndex = (siteLon - LON_START) / 0.5
        latIndex = (siteLat - LAT_START) / 0.5

        filepath = MET_PATH + '/' + str(i+1) + MET_SUFFIX
        if path.exists(filepath):
            siteData = pandas.read_csv(filepath, sep='\s+', usecols=np.arange(2, 9), header=3)
            tminVariable[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [0]]).reshape(TIME_SPAN)
            tdayVariable[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [1]]).reshape(TIME_SPAN)
            tmaxVariable[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [2]]).reshape(TIME_SPAN)
            prcpVariable[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [3]]).reshape(TIME_SPAN)
            vpdVariable[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [4]]).reshape(TIME_SPAN)
            sradVariable[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [5]]).reshape(TIME_SPAN)
            daylenVariable[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [6]]).reshape(TIME_SPAN)
            print(i+1, SITENUM)
    dataset.close()
    print('finished!')

writeNC()
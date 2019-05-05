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

def writeNC():
    if path.exists(IBIS_NC_PATH):
        remove(IBIS_NC_PATH)

    dataset = nc.Dataset(IBIS_NC_PATH, 'w', format='NETCDF4')

    lonDimension = dataset.createDimension('long', len(LONS))
    latDimension = dataset.createDimension('lat', len(LATS))
    timeDimension = dataset.createDimension('time', None)

    lonVariable = dataset.createVariable("long", 'f4', ("long"))
    latVariable = dataset.createVariable("lat", 'f4', ("lat"))
    timeVariable = dataset.createVariable("time", 'f4', ("time"))

    gppVariable = dataset.createVariable('GPP', 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=4)
    nppVariable = dataset.createVariable('NPP', 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=4)
    neeVariable = dataset.createVariable('NEE', 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=4)

    # gppVariable.set_auto_mask(True)
    # nppVariable.set_auto_mask(True)
    # neeVariable.set_auto_mask(True)
    # gppVariable.setncattr('missing_value', 0)
    # nppVariable.setncattr('missing_value', 0)
    # neeVariable.setncattr('missing_value', 0)

    lonDimension = dataset.dimensions['long']
    latDimension = dataset.dimensions['lat']
    timeDimension = dataset.dimensions['time']

    lonVariable = dataset.variables['long']
    latVariable = dataset.variables['lat']
    timeVariable = dataset.variables['time']
    gppVariable = dataset.variables['GPP']
    nppVariable = dataset.variables['NPP']
    neeVariable = dataset.variables['NEE']

    lonVariable.units = 'degrees_east'
    latVariable.units = 'degrees_north'
    timeVariable.units = 'days since ' + str(TIME_START) + '-01-01'
    timeVariable.calendar = '365_day'
    # gppVariable.units = 'kgC m-2 y-1'
    # nppVariable.units = 'gC m-2 y-1'
    # neeVariable.units = 'gC m-2 y-1'

    lonVariable[:] = LONS
    latVariable[:] = LATS
    timeLen = YEAR_NUM
    timeStep = 365
    timeVariable[:] = [n* timeStep for n in range(timeLen)]

    lanNum=int((LAT_END-LAT_START)/GRID_LENGTH)
    LON_NUM=int((LON_END-LON_START)/GRID_LENGTH)
    gpp = np.empty([YEAR_NUM, lanNum, LON_NUM])
    npp = np.empty([YEAR_NUM, lanNum, LON_NUM])
    nee = np.empty([YEAR_NUM, lanNum, LON_NUM])
    logFile = open(IBIS_ERR_PATH, 'w')
    for i in range(SITENUM):
        siteCoorStr = linecache.getline(COOR_PATH, i+1)
        lonLat = re.split('\s+', siteCoorStr)
        siteLon = float(lonLat[0])
        siteLat = float(lonLat[1])
        lonIndex = int((siteLon - LON_START) / 0.5)
        latIndex = int((siteLat - LAT_START) / 0.5)
        filepath = IBIS_OUT_PATH + '/' + str(i+1) + IBIS_OUT_SUFFIX
        if path.exists(filepath):
            try:
                # siteData = pandas.read_csv(filepath, sep='\s+', usecols=[1], header=None)
                siteData = pandas.read_csv(filepath, sep='\s+', usecols=[1, 2, 3], header=None)
                col1 = pandas.to_numeric(siteData.iloc[:, 0], errors='coerce')
                col2 = pandas.to_numeric(siteData.iloc[:, 1], errors='coerce')
                col3 = pandas.to_numeric(siteData.iloc[:, 2], errors='coerce')
                # col1 = pandas.to_numeric(siteData.iloc[:, 0], errors='coerce')
                # col2 = pandas.to_numeric(siteData.iloc[:, 1], errors='coerce')
                # col3 = pandas.to_numeric(siteData.iloc[:, 2], errors='coerce')
                # gpp[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [0]]).reshape(32)
                # npp[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [1]]).reshape(32)
                # nee[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [2]]).reshape(32)
                # gpp[:, latIndex, lonIndex] = np.resize(col1,timeLen).reshape(YEAR_NUM, -1).mean(axis=1)*1000
                gpp[:, latIndex, lonIndex] = col1
                npp[:, latIndex, lonIndex] = col2
                nee[:, latIndex, lonIndex] = col3
                print(i+1, SITENUM)
            except Exception as instance:
                print(instance)
                print('****** %s failed' % str(i+1))
                logFile.write('%4s failed\n' % str(i+1))
    gppVariable[:] = gpp
    nppVariable[:] = npp
    neeVariable[:] = nee

    # gppVariable[:] = np.ma.masked_where((gppVariable[:] < 0) | (gppVariable[:] == 0) | (gppVariable[:] == missing_value), gppVariable)
    # nppVariable[:] = np.ma.masked_where((nppVariable[:] < 0) | (nppVariable[:] == 0) | (nppVariable[:] == missing_value), nppVariable)
    # neeVariable[:] = np.ma.masked_where((neeVariable[:] < -100) | (neeVariable[:] == 0) | (neeVariable[:] == missing_value), neeVariable)
    # 这里必须mask掉，要不然在geoserver里 海洋全部不透明
    gppVariable[:] = np.ma.masked_where((gppVariable[:] == 0), gppVariable)
    nppVariable[:] = np.ma.masked_where((gppVariable[:] == 0), gppVariable)
    neeVariable[:] = np.ma.masked_where((gppVariable[:] == 0), gppVariable)
    # nppVariable[:] = np.ma.masked_where((nppVariable[:] <= 0), nppVariable)
    # neeVariable[:] = np.ma.masked_where((neeVariable[:] == 0) | (neeVariable[:]>3000) | (neeVariable[:]<-3000), neeVariable)
    
    dataset.close()
    logFile.close()
    print('finished!')

# readNC()
writeNC()

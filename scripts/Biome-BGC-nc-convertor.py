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
DATA_HOME='/home/scr/Data'
COOR_PATH = DATA_HOME + '/IBIS_Data/5b9012e4c29ca433443dcfab/IBIS_site_info.txt'

BIOME_OUT_PATH = DATA_HOME + '/Biome_BGC_Data/5b9012e4c29ca433443dcfab/outputs'
BIOME_OUT_SUFFIX = '.annual.ascii'
BIOME_NC_PATH = 'data/Biome-BGC-out.nc'

IBIS_OUT_PATH = DATA_HOME + '/IBIS_Data/5b9012e4c29ca433443dcfab/outputs'
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
    dataset = nc.Dataset(BIOME_NC_PATH, 'r+', format='NETCDF4')

    lonDimension = dataset.dimensions['long']
    latDimension = dataset.dimensions['lat']
    timeDimension = dataset.dimensions['time']

    lonVariable = dataset.variables['long']
    latVariable = dataset.variables['lat']
    timeVariable = dataset.variables['time']
    gppVariable = dataset.variables['GPP']
    nppVariable = dataset.variables['NPP']
    nepVariable = dataset.variables['NEP']
    neeVariable = dataset.variables['NEE']

    timeVariable.datatype = 'f4'
    timeVariable.units = 'days since ' + str(TIME_START) + '-01-01'
    timeVariable.calendar = '365_day'

    lonVariable[:] = lons
    latVariable[:] = lats
    # dates = [datetime(TIME_START, 1, 1) + n * timedelta(days=1) for n in range(TIME_SPAN)]
    # timeVariable[:] = date2num(dates, units=timeVariable.units, calendar=timeVariable.calendar)
    timeVariable[:] = [n * 365 for n in range(TIME_SPAN)]

    dataset.close()
    print('finished!')

def writeNC():
    if path.exists(BIOME_NC_PATH):
        remove(BIOME_NC_PATH)
    # chmod(BIOME_NC_PATH, stat.S_IRWXO)
    # chmod(BIOME_NC_PATH, stat.S_IRWXG)
    # chmod(BIOME_NC_PATH, stat.S_IRWXU)

    dataset = nc.Dataset(BIOME_NC_PATH, 'w', format='NETCDF4')

    lonDimension = dataset.createDimension('long', len(lons))
    latDimension = dataset.createDimension('lat', len(lats))
    timeDimension = dataset.createDimension('time', None)

    lonVariable = dataset.createVariable("long", 'f4', ("long"))
    latVariable = dataset.createVariable("lat", 'f4', ("lat"))
    timeVariable = dataset.createVariable("time", 'f4', ("time"))

    gppVariable = dataset.createVariable('GPP', 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=3)
    nppVariable = dataset.createVariable('NPP', 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=3)
    nepVariable = dataset.createVariable('NEP', 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=3)
    neeVariable = dataset.createVariable('NEE', 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=3)

    lonDimension = dataset.dimensions['long']
    latDimension = dataset.dimensions['lat']
    timeDimension = dataset.dimensions['time']

    lonVariable = dataset.variables['long']
    latVariable = dataset.variables['lat']
    timeVariable = dataset.variables['time']
    gppVariable = dataset.variables['GPP']
    nppVariable = dataset.variables['NPP']
    nepVariable = dataset.variables['NEP']
    neeVariable = dataset.variables['NEE']

    lonVariable.units = 'degrees_east'
    latVariable.units = 'degrees_north'
    timeVariable.units = 'days since ' + str(TIME_START) + '-01-01'
    timeVariable.calendar = '365_day'
    gppVariable.setncattr('missing_value', -99999)

    lonVariable[:] = lons
    latVariable[:] = lats
    # dates = [datetime(TIME_START, 1, 1) + n * timedelta(days=1) for n in range(TIME_SPAN)]
    # timeVariable[:] = date2num(dates, units=timeVariable.units, calendar=timeVariable.calendar)
    timeVariable[:] = [n*365 for n in range(TIME_SPAN)]

    # for i in range(SITENUM):
    #     siteCoorStr = linecache.getline(COOR_PATH, i+1)
    #     lonLat = re.split('\s+', siteCoorStr)
    #     siteLon = float(lonLat[0])
    #     siteLat = float(lonLat[1])
    #     lonIndex = (siteLon - LON_START) / 0.5
    #     latIndex = (siteLat - LAT_START) / 0.5
    #     gppVariable[:, latIndex, lonIndex] = np.random.random(TIME_SPAN)*10
    #     # gppVariable[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [0]])
    #     # nppVariable[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [1]])
    #     # nepVariable[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [2]])
    #     print(i+1, SITENUM)

    for i in range(SITENUM):
        siteCoorStr = linecache.getline(COOR_PATH, i+1)
        lonLat = re.split('\s+', siteCoorStr)
        siteLon = float(lonLat[0])
        siteLat = float(lonLat[1])
        lonIndex = (siteLon - LON_START) / 0.5
        latIndex = (siteLat - LAT_START) / 0.5
        filepath = BIOME_OUT_PATH + '/' + str(i+1) + BIOME_OUT_SUFFIX
        if path.exists(filepath):
            siteData = pandas.read_csv(filepath, sep='\s+', usecols=[0, 1, 2, 3], header=None)
            gppVariable[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [0]])
            nppVariable[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [1]])
            nepVariable[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [2]])
            neeVariable[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [3]])
            print(i+1, SITENUM)
    dataset.close()
    print('finished!')

# readNC()
writeNC()

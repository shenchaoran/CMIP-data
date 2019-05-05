import netCDF4 as nc
from os import path,chmod, remove
import stat
import numpy as np
import csv
import pandas
import re
import linecache
import time

SITENUM = 61353
DATA_HOME='/home/scr/Data'
COOR_PATH = DATA_HOME + '/IBIS_Data/5b9012e4c29ca433443dcfab/IBIS_site_info.txt'

BIOME_OUT_PATH = DATA_HOME + '/Biome_BGC_Data/5b9012e4c29ca433443dcfab/outputs'
BIOME_OUT_SUFFIX = '.annual-avg.ascii'
BIOME_NC_PATH = 'data/Biome-BGC-annual-output.nc'

IBIS_OUT_PATH = DATA_HOME + '/IBIS_Data/5b9012e4c29ca433443dcfab/outputs'
IBIS_OUT_SUFFIX = '.annual.txt'
IBIS_NC_PATH = 'data/IBIS-annual-out.nc'

LPJ_OUT_PATH = DATA_HOME + '/LPJ/5b9012e4c29ca433443dcfab/outputs'
LPJ_OUT_SUFFIX = '.daily.ascii'
LPJ_NC_PATH = 'data/LPJ-annual-out.nc'
grid_path = DATA_HOME + '/LPJ/5b9012e4c29ca433443dcfab/grid/'
grid_suffix = '_grid.ascii'

GRID_LENGTH = 0.5
LON_START = -179.75
LON_END = 179.75 + GRID_LENGTH
LAT_START = -54.75
LAT_END = 82.25 + GRID_LENGTH
LAT_COUNT = (LAT_END-LAT_START)/GRID_LENGTH
LON_COUNT = (LON_END-LON_START)/GRID_LENGTH

YEAR_NUM = 32
TIME_START = 1982
TIME_END = TIME_START + YEAR_NUM

LONS = np.arange(LON_START, LON_END, GRID_LENGTH)
LATS = np.arange(LAT_START, LAT_END, GRID_LENGTH)

def readNC():
    # chmod(LPJ_NC_PATH, stat.S_IRWXU)
    # chmod(LPJ_NC_PATH, stat.S_IRWXG)
    # chmod(LPJ_NC_PATH, stat.S_IRWXO)

    dataset = nc.Dataset(LPJ_NC_PATH, 'r+', format='NETCDF4')

    lonDimension = dataset.dimensions['long']
    latDimension = dataset.dimensions['lat']
    timeDimension = dataset.dimensions['time']

    lonVariable = dataset.variables['long']
    latVariable = dataset.variables['lat']
    timeVariable = dataset.variables['time']
    gppVariable = dataset.variables['GPP']
    nppVariable = dataset.variables['NPP']
    # nepVariable = dataset.variables['NEP']
    # neeVariable = dataset.variables['NEE']


    # timeVariable.datatype = 'f4'
    # timeVariable.units = 'days since ' + str(TIME_START) + '-01-01'
    # timeVariable.calendar = '365_day'

    # lonVariable[:] = LONS
    # latVariable[:] = LATS
    # timeVariable[:] = [n * 365 for n in range(YEAR_NUM)]

    dataset.close()
    print('finished!')

def writeNC():
    if path.exists(LPJ_NC_PATH):
        remove(LPJ_NC_PATH)
    # chmod(LPJ_NC_PATH, stat.S_IRWXO)
    # chmod(LPJ_NC_PATH, stat.S_IRWXG)
    # chmod(LPJ_NC_PATH, stat.S_IRWXU)

    dataset = nc.Dataset(LPJ_NC_PATH, 'w', format='NETCDF4')

    lonDimension = dataset.createDimension('long', len(LONS))
    latDimension = dataset.createDimension('lat', len(LATS))
    timeDimension = dataset.createDimension('time', None)

    lonVariable = dataset.createVariable("long", 'f4', ("long"))
    latVariable = dataset.createVariable("lat", 'f4', ("lat"))
    timeVariable = dataset.createVariable("time", 'f4', ("time"))

    gppVariable = dataset.createVariable('GPP', 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=4)
    nppVariable = dataset.createVariable('NPP', 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=4)

    # gppVariable.set_auto_mask(True)
    # nppVariable.set_auto_mask(True)
    # nepVariable.set_auto_mask(True)
    # neeVariable.set_auto_mask(True)
    # gppVariable.setncattr('missing_value', 0)
    # nppVariable.setncattr('missing_value', 0)
    # nepVariable.setncattr('missing_value', 0)
    # neeVariable.setncattr('missing_value', 0)

    lonDimension = dataset.dimensions['long']
    latDimension = dataset.dimensions['lat']
    timeDimension = dataset.dimensions['time']

    lonVariable = dataset.variables['long']
    latVariable = dataset.variables['lat']
    timeVariable = dataset.variables['time']
    gppVariable = dataset.variables['GPP']
    nppVariable = dataset.variables['NPP']

    lonVariable.units = 'degrees_east'
    latVariable.units = 'degrees_north'
    timeVariable.units = 'days since ' + str(TIME_START) + '-01-01'
    timeVariable.calendar = '365_day'

    lonVariable[:] = LONS
    latVariable[:] = LATS
    timeVariable[:] = [n*365 for n in range(YEAR_NUM)]

    lanNum=int((LAT_END-LAT_START)/GRID_LENGTH)
    LON_NUM=int((LON_END-LON_START)/GRID_LENGTH)
    gpp = np.empty([YEAR_NUM, lanNum, LON_NUM])
    npp = np.empty([YEAR_NUM, lanNum, LON_NUM])
    for i in range(SITENUM):
        siteCoorStr = linecache.getline(grid_path + str(i + 1) + grid_suffix , 1)
        lonLat = re.split('\s+', siteCoorStr)
        siteLon = float(lonLat[0])
        siteLat = float(lonLat[1])
        lonIndex = int((siteLon - LON_START) / 0.5)
        latIndex = int((siteLat - LAT_START) / 0.5)
        if (latIndex < LAT_COUNT) and (latIndex >= 0) and (lonIndex < LON_COUNT) and(lonIndex >=0):
            filepath = LPJ_OUT_PATH + '/' + str(i+1) + LPJ_OUT_SUFFIX
            if path.exists(filepath):
                siteData = pandas.read_csv(filepath, sep='\s+', header=None)
                colNPP = np.array(siteData.iloc[:, [0]]).reshape(32, -1).mean(axis=1)
                colGPP = np.array(siteData.iloc[:, [1]]).reshape(32, -1).mean(axis=1)
                npp[:, latIndex, lonIndex] = colNPP
                gpp[:, latIndex, lonIndex] = colGPP
            print(i+1, SITENUM)
        else:
            # 范围是 [1,61233]
            print('out of range: ', i+1)
    gppVariable[:] = gpp
    nppVariable[:] = npp

    gppVariable[:] = np.ma.masked_where((gppVariable[:] == 0), gppVariable)
    nppVariable[:] = np.ma.masked_where((nppVariable[:] == 0), nppVariable)
    
    dataset.close()
    print('finished!')

# readNC()
writeNC()

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
BIOME_NC_PATH = 'data/Biome-BGC-annual-output.nc'

IBIS_OUT_PATH = DATA_HOME + '/IBIS_Data/5b9012e4c29ca433443dcfab/outputs'
IBIS_OUT_SUFFIX = '.annual.txt'
IBIS_NC_PATH = 'data/IBIS-annual-out.nc'

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
    # chmod(BIOME_NC_PATH, stat.S_IRWXU)
    # chmod(BIOME_NC_PATH, stat.S_IRWXG)
    # chmod(BIOME_NC_PATH, stat.S_IRWXO)

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


    # timeVariable.datatype = 'f4'
    # timeVariable.units = 'days since ' + str(TIME_START) + '-01-01'
    # timeVariable.calendar = '365_day'

    # lonVariable[:] = lons
    # latVariable[:] = lats
    # timeVariable[:] = [n * 365 for n in range(TIME_SPAN)]

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

    gppVariable = dataset.createVariable('GPP', 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=8)
    nppVariable = dataset.createVariable('NPP', 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=8)
    nepVariable = dataset.createVariable('NEP', 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=8)
    neeVariable = dataset.createVariable('NEE', 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=8)

    gppVariable.set_auto_mask(True)
    nppVariable.set_auto_mask(True)
    nepVariable.set_auto_mask(True)
    neeVariable.set_auto_mask(True)
    gppVariable.setncattr('missing_value', 0)
    nppVariable.setncattr('missing_value', 0)
    nepVariable.setncattr('missing_value', 0)
    neeVariable.setncattr('missing_value', 0)

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

    lonVariable[:] = lons
    latVariable[:] = lats
    timeVariable[:] = [n*365 for n in range(TIME_SPAN)]

    lanNum=int((LAT_END-LAT_START)/GRID_LENGTH)
    lonNum=int((LON_END-LON_START)/GRID_LENGTH)
    gpp = np.empty([TIME_SPAN, lanNum, lonNum])
    npp = np.empty([TIME_SPAN, lanNum, lonNum])
    nep = np.empty([TIME_SPAN, lanNum, lonNum])
    nee = np.empty([TIME_SPAN, lanNum, lonNum])
    for i in range(SITENUM):
        siteCoorStr = linecache.getline(COOR_PATH, i+1)
        lonLat = re.split('\s+', siteCoorStr)
        siteLon = float(lonLat[0])
        siteLat = float(lonLat[1])
        lonIndex = int((siteLon - LON_START) / 0.5)
        latIndex = int((siteLat - LAT_START) / 0.5)
        filepath = BIOME_OUT_PATH + '/' + str(i+1) + BIOME_OUT_SUFFIX
        if path.exists(filepath):
            siteData = pandas.read_csv(filepath, sep='\s+', usecols=[0, 1, 2, 3], header=None)
            gpp[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [0]]).reshape(32)*365000
            npp[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [1]]).reshape(32)*365000
            nep[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [2]]).reshape(32)*365000
            nee[:, latIndex, lonIndex] = np.array(siteData.iloc[:, [3]]).reshape(32)*365000
            print(i+1, SITENUM)
    gppVariable[:] = gpp
    nppVariable[:] = npp
    nepVariable[:] = nep
    neeVariable[:] = nee


    # gppVariable.scale_factor=365000
    # gppVariable.add_offset=0
    # nppVariable.scale_factor=365000
    # nppVariable.add_offset=0
    # nepVariable.scale_factor=365000
    # nepVariable.add_offset=0
    # neeVariable.scale_factor=365000
    # neeVariable.add_offset=0
    
    dataset.close()
    print('finished!')

# readNC()
writeNC()

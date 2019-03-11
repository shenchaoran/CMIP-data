import netCDF4 as nc
from os import path,chmod, remove
import stat
import numpy as np
import csv
import pandas
import re
import linecache
import time
from scipy.interpolate import interp1d

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
srcPath = folder + '8-MOD17A2.nc'
distPaths = [
    folder + '32-MOD17A2.nc',
    folder + '365-MOD17A2.nc',
    folder + '2000-2013-avg-MOD17A2.nc',
    folder + '32-avg-MOD17A2.nc',
]

srcDataset = nc.Dataset(srcPath, 'r', format='NETCDF4')
gpp_src_var = srcDataset.variables['GPP']
for i, dPath in enumerate(distPaths):
    if i < 3:
        continue
    ds = nc.Dataset(dPath, 'w', format='NETCDF4')
    ds.createDimension('long', lonNum)
    ds.createDimension('lat', latNum)
    lonVariable = ds.createVariable("long", 'f4', ("long"))
    latVariable = ds.createVariable("lat", 'f4', ("lat"))
    lonVariable.units = 'degrees_east'
    latVariable.units = 'degrees_north'
    if i != 2:
        ds.createDimension('time', None)
        timeVariable = ds.createVariable("time", 'f4', ("time"))
        timeVariable.units = 'days since 2000-01-01'
        timeVariable.calendar = '365_day'
        gppVariable = ds.createVariable("GPP", 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=4)
    else:
        gppVariable = ds.createVariable("GPP", 'f4', ('lat', 'long'), zlib=True, least_significant_digit=4)
    lonVariable[:] = lons
    latVariable[:] = lats
    if i == 0:
        timeVarLen = int(16*12)
        timeVariable[:] = [n*30 for n in range(timeVarLen)]
        tmp = gpp_src_var[:].reshape(16, 46, latNum, lonNum)
        data = np.empty([16, 12, latNum, lonNum])
        for j in range(16):
            for k in range(11):
                data[j, k,:,:] = tmp[j, k*4:(k+1)*4,:,:].mean(axis=0)
            data[j, 11,:,:] = tmp[j, -4:,:,:].mean(axis=0)

        data = data.reshape(-1, latNum, lonNum)
        gppVariable.units = 'gC m-2 d-1'
    elif i == 1:
        timeVarLen = 16
        timeVariable[:] = [n*365 for n in range(timeVarLen)]
        data = gpp_src_var[:].reshape(16, 46, latNum, lonNum).mean(axis=1)*.365
        gppVariable.units = 'kgC m-2 y-1'
    elif i == 2:
        data = gpp_src_var[:14*46].mean(axis=0)*.365
        gppVariable.units = 'kgC m-2 y-1'
    elif i == 3:
        timeVarLen = 12
        timeVariable[:] = [n*30 for n in range(timeVarLen)]
        tmp = gpp_src_var[:].reshape(16, 46, latNum, lonNum).mean(axis=0)
        data = np.empty([12, latNum, lonNum])
        for j in range(11):
            data[j] = tmp[j*4: (j+1)*4].mean(axis=0)
        data[11] = tmp[-4:].mean(axis=0)
        # data = np.resize(gpp_src_var, (4*12*16, latNum, lonNum)) \
        #     .reshape(4*12, 16, latNum, lonNum).mean(axis=1) \
        #     .reshape(4, 12, latNum, lonNum).mean(axis=0)
        gppVariable.units = 'gC m-2 d-1'
    gppVariable[:] = data
    gppVariable[:] = np.ma.masked_where((gppVariable[:] < 0.00001), gppVariable)
    # if gppVariable.units == 'gC m-2 d-1':
    #     gppVariable[:] = np.ma.masked_where((gppVariable[:] == 0) | (gppVariable[:] > 10), gppVariable)
    # elif gppVariable.units == 'kgC m-2 y-1':
    #     gppVariable[:] = np.ma.masked_where(((gppVariable[:] == 0) | (gppVariable[:] > 3.5)), gppVariable)
    ds.close()
    print('%s finished!' % dPath)

srcDataset.close()
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
from CMIP import *

folder = '/home/scr/Data/scripts/data/'
srcPath = folder + '8-days/8-MOD17A2.nc'
distPaths = [
    folder + 'month/MOD17A2.nc',
    folder + 'annual/MOD17A2.nc',
    folder + 'annual/MOD17A2-avg.nc',
    folder + 'month/MOD17A2-avg.nc',
]

srcDataset = nc.Dataset(srcPath, 'r', format='NETCDF4')
gpp_src_var = srcDataset.variables['GPP']
for i, dPath in enumerate(distPaths):
    ds = nc.Dataset(dPath, 'w', format='NETCDF4')
    ds.createDimension('long', LON_NUM)
    ds.createDimension('lat', LAT_NUM)
    lonVariable = ds.createVariable("long", 'f4', ("long"))
    latVariable = ds.createVariable("lat", 'f4', ("lat"))
    lonVariable.units = 'degrees_east'
    latVariable.units = 'degrees_north'
    if i != 2:
        ds.createDimension('time', None)
        timeVariable = ds.createVariable("time", 'f4', ("time"))
        timeVariable.units = 'days since %s-01-01' % str(MOD17A2_START)
        timeVariable.calendar = '365_day'
        gppVariable = ds.createVariable("GPP", 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=4)
    else:
        gppVariable = ds.createVariable("GPP", 'f4', ('lat', 'long'), zlib=True, least_significant_digit=4)
    lonVariable[:] = LONS
    latVariable[:] = LATS
    if i == 0:
        timeVarLen = int(MOD17A2_YEAR_NUM*12)
        timeVariable[:] = [n*30 for n in range(timeVarLen)]
        tmp = gpp_src_var[:].reshape(MOD17A2_YEAR_NUM, 46, LAT_NUM, LON_NUM)
        data = np.empty([MOD17A2_YEAR_NUM, 12, LAT_NUM, LON_NUM])
        for j in range(MOD17A2_YEAR_NUM):
            for k in range(11):
                data[j, k,:,:] = tmp[j, k*4:(k+1)*4,:,:].mean(axis=0)
            data[j, 11,:,:] = tmp[j, -4:,:,:].mean(axis=0)

        data = data.reshape(-1, LAT_NUM, LON_NUM)
        gppVariable.units = 'gC m-2 d-1'
    elif i == 1:
        timeVarLen = MOD17A2_YEAR_NUM
        timeVariable[:] = [n*365 for n in range(timeVarLen)]
        data = gpp_src_var[:].reshape(MOD17A2_YEAR_NUM, 46, LAT_NUM, LON_NUM).mean(axis=1)*.365
        gppVariable.units = 'kgC m-2 y-1'
    elif i == 2:
        data = gpp_src_var[:].mean(axis=0)*.365
        gppVariable.units = 'kgC m-2 y-1'
    elif i == 3:
        timeVarLen = 12
        timeVariable[:] = [n*30 for n in range(timeVarLen)]
        tmp = gpp_src_var[:].reshape(MOD17A2_YEAR_NUM, 46, LAT_NUM, LON_NUM).mean(axis=0)
        data = np.empty([12, LAT_NUM, LON_NUM])
        for j in range(11):
            data[j] = tmp[j*4: (j+1)*4].mean(axis=0)
        data[11] = tmp[-4:].mean(axis=0)
        gppVariable.units = 'gC m-2 d-1'
    gppVariable[:] = np.ma.filled(data, fill_value=0)
    ds.close()
    print('%s finished!' % dPath)

srcDataset.close()
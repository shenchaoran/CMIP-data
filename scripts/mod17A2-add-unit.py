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

folder = '/home/scr/Data/scripts/data/'
ncPath = folder + '8-MOD17A2.nc'

ds = nc.Dataset(ncPath, 'r+', format='NETCDF4')
gppVar = ds.variables['GPP']
gppVar.units = 'gC m-2 d-1'

ds.close()
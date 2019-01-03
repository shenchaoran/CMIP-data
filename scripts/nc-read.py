import netCDF4 as nc
from os import path
import numpy as np
import csv
import pandas
import re
import linecache
import time
from datetime import datetime, timedelta
from netCDF4 import num2date, date2num, date2index

dataset = nc.Dataset('data/cld.mon.nc','r+',format='NETCDF4')
dataset.history = 'Created ' + time.ctime(time.time())

dataset.close()
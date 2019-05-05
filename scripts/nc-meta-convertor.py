import netCDF4 as nc
from os import path, chmod, remove, mkdir
import sys, getopt, stat
from math import ceil, floor
import numpy as np
import csv
import pandas as pd
import re
import linecache
import time
import matplotlib.pyplot as plt
import matplotlib
from multiprocessing import Pool, sharedctypes, RawArray, RawValue
plt.switch_backend('tkagg')

SITENUM = 40595
DATA_HOME='/home/scr/Data'
COOR_PATH = DATA_HOME + '/IBIS_Data/5b9012e4c29ca433443dcfab/IBIS_site_info.txt'
GRID_LENGTH = 0.5
LON_START = -179.75
LON_END = 179.75 + GRID_LENGTH
LAT_START = -54.75
LAT_END = 82.25 + GRID_LENGTH
LAN_NUM=int((LAT_END-LAT_START)/GRID_LENGTH)
LON_NUM=int((LON_END-LON_START)/GRID_LENGTH)
YEAR_NUM = 32
TIME_START = 1982
TIME_END = TIME_START + YEAR_NUM
LONS = np.arange(LON_START, LON_END, GRID_LENGTH)
LATS = np.arange(LAT_START, LAT_END, GRID_LENGTH)

options, args = getopt.getopt(sys.argv[1:], '', ['model=', 'time='])
for opt in options:
    if(opt[0] == '--model'):
        model = opt[1]
    if(opt[0] == '--time'):
        time = opt[1]
folder = './data/%s-%s' % (model, time)
fpath = '%s/%s.nc' % (folder, model)
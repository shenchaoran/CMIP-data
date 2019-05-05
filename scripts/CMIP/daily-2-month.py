# TODO
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
from MS.IBIS import *
from MS.LPJ import *
from MS.Biome_BGC import *
from CMIP import *
plt.switch_backend('tkagg')

counter = RawValue('i')
counter.value = 0
failed_counter = RawValue('i')
failed_counter.value = 0
test = False
options, args = getopt.getopt(sys.argv[1:], '', ['model=', 'test='])
for opt in options:
    if(opt[0] == '--model'):
        if opt[1] == 'IBIS':
            ms_daily = IBIS('daily')
            ms_month = IBIS('month')
        elif opt[1] == 'Biome-BGC':
            ms_daily = Biome_BGC('daily')
            ms_month = Biome_BGC('month')
        elif opt[1] == 'LPJ':
            ms_daily = LPJ('daily')
            ms_month = LPJ('month')
        else:
            print('invalid model option')
            sys.exit(1) 
    elif(opt[0] == '--test'):
        test = True 

def convert2Month(i):
    try:
        counter.value += 1
        print('counter: %s    %5.2f%%    site index: %s' % (str(counter.value), counter.value*100/40595, str(i)))
        srcPath = '%s/%s%s' % (ms_daily.folder, str(i), ms_daily.suffix)
        distPath = '%s/%s%s' % (ms_month.folder, str(i), ms_month.suffix)
        if path.exists(distPath):
            fsize = path.getsize(distPath)
            if fsize > 0:
                rerun = False
            else:
                rerun = True
        else:
            rerun = True
        if rerun:
            df = pd.read_csv(srcPath, sep='\s+', usecols=ms_daily.to_month_usecols, header=None, na_values='***************')
            # (time, var)
            df = df.replace(to_replace='\*+', value='0', regex=True)
            for i, column in enumerate(df.columns):
                df[[column]] = df[[column]].astype('float64')
            df_shape = df.shape
            dist_ndarr = np.empty((YEAR_NUM, 12, df_shape[1]))
            data = np.resize(np.array(df), YEAR_NUM*365*df_shape[1]).reshape(YEAR_NUM, -1, df_shape[1])
            for j in range(YEAR_NUM):
                dist_ndarr[j,:,:] = np.resize(data[j], df_shape[1] * 12 * 30).reshape(12, 30, df_shape[1]).mean(axis=1)
            dist_ndarr = dist_ndarr.reshape(-1, df_shape[1])
            np.savetxt(distPath, dist_ndarr, delimiter=' ', fmt='%16.8f')
    except Exception as instance:
        failed_counter.value += 1
        print(i, instance)

if test:
    convert2Month(36978)
else:
    t1 = time.time()
    pool = Pool(processes=30)
    pool.map(convert2Month, np.arange(40595) + 1)
    pool.close()
    pool.join()
    t2 = time.time()
    unit = 's'
    duration = int(t2-t1)
    if duration > 60:
        duration /= 60
        unit = 'min'
    if duration > 60:
        duration /= 60
        unit = 'hour'
    print('执行时间：%4.2f %s' % (duration, unit))
    print('失败个数：%d' % (failed_counter.value))
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

cols = [
    {
        "id": "adrain",
        "type": "",
        "description": "daily average rainfall rate",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "mm d-1",
        "metricName": "daily-average-rainfall-rate"
    }, {
        "id": "adsnow",
        "type": "",
        "description": "daily average snowfall rate",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "mm d-1",
        "metricName": "daily-average-snowfall-rate"
    }, {
        "id": "adaet",
        "type": "",
        "description": "daily average aet",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "mm d-1",
        "metricName": "daily-average-aet"
    }, {
        "id": "adtrans",
        "type": "",
        "description": "",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "unknown",
        "metricName": ""
    }, {
        "id": "adinvap",
        "type": "",
        "description": "",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "unknown",
        "metricName": ""
    }, {
        "id": "adsuvap",
        "type": "",
        "description": "",
        "scale": 1000.0,
        "offset": 0.0,
        "unit": "unknown",
        "metricName": ""
    }, {
        "id": "adtrunoff",
        "type": "",
        "description": "daily average total runoff",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "mm d-1",
        "metricName": "daily-average-total-runoff"
    }, {
        "id": "adsrunoff",
        "type": "",
        "description": "daily average surface runoff",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "mm d-1",
        "metricName": "daily-average-surface-runoff"
    }, {
        "id": "addrainage",
        "type": "",
        "description": "daily average drainage",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "mm d-1",
        "metricName": "daily-average-drainage"
    }, {
        "id": "adrh",
        "type": "",
        "description": "daily average relative humidity",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "percent",
        "metricName": "daily-average-rh"
    }, {
        "id": "adsnod",
        "type": "",
        "description": "daily average snow depth",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "m",
        "metricName": "daily-average-snow-depth"
    }, {
        "id": "adsnof",
        "type": "",
        "description": "daily average snow fraction",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "fraction",
        "metricName": "daily-average-snow-fraction"
    }, {
        "id": "adwsoi",
        "type": "",
        "description": "daily average soil moisture",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "fraction",
        "metricName": "daily-average-soil-moisture"
    }, {
        "id": "adwisoi",
        "type": "",
        "description": "daily average soil ice",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "fraction",
        "metricName": "daily-average-soil-ice"
    }, {
        "id": "adtsoi",
        "type": "",
        "description": "daily average soil temperature",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "°C",
        "metricName": "daily-average-soil-temperature"
    }, {
        "id": "adwsoic",
        "type": "",
        "description": "daily average soil moisture using root profile weighting",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "fraction",
        "metricName": "daily-average-soil-moisture-using-root-profile-weighting"
    }, {
        "id": "adtsoic",
        "type": "",
        "description": "daily average soil temperature using profile weighting",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "°C",
        "metricName": "daily-average-soil-temperature-using-profile-weighting"
    }, {
        "id": "adco2mic",
        "type": "",
        "description": "daily accumulated co2 respiration from microbes",
        "scale": 1000.0,
        "offset": 0.0,
        "unit": "kgN m-2 d-1",
        "metricName": "daily-accumulated-co2-respiration-from-microbes"
    }, {
        "id": "adco2root",
        "type": "",
        "description": "daily accumulated co2 respiration from roots",
        "scale": 1000.0,
        "offset": 0.0,
        "unit": "kgC m-2 d-1",
        "metricName": "daily-accumulated-co2-respiration-from-roots"
    }, {
        "id": "adco2soi",
        "type": "",
        "description": "daily accumulated co2 respiration from soil(total)",
        "scale": 1000.0,
        "offset": 0.0,
        "unit": "kgC m-2 d-1",
        "metricName": "daily-accumulated-co2-respiration-from-soil(total)"
    }, {
        "id": "adco2ratio",
        "type": "",
        "description": "ratio of root to total co2 respiration",
        "scale": 1000.0,
        "offset": 0.0,
        "unit": "kgC m-2 d-1",
        "metricName": "ratio-of-root-to-total-co2-respiration"
    }, {
        "id": "adnmintot",
        "type": "",
        "description": "daily accumulated net nitrogen mineralization",
        "scale": 1000.0,
        "offset": 0.0,
        "unit": "kgN m-2 d-1",
        "metricName": "daily-accumulated-net-nitrogen-mineralization"
    }, {
        "id": "adtlaysoi",
        "type": "",
        "description": "daily average soil temperature of top layer",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "°C",
        "metricName": "daily-average-soil-temperature-of-top-layer"
    }, {
        "id": "adwlaysoi",
        "type": "",
        "description": "daily average soil moisture of top layer",
        "scale": 1.0,
        "offset": 0.0,
        "unit": "fraction",
        "metricName": "daily-average-soil-moisture-of-top-layer"
    }, {
        "id": "adneetot",
        "type": "",
        "description": "daily accumulated net ecosystem exchange of co2 in ecosystem",
        "scale": 1000.0,
        "offset": 0.0,
        "unit": "kgC m-2 d-1",
        "metricName": "daily-average-NEE"
    }, {
        "id": "adgpptot",
        "type": "",
        "description": "daily average GPP",
        "scale": 1000.0,
        "offset": 0.0,
        "unit": "kgC m-2 d-1",
        "metricName": "daily-average-GPP"
    }, {
        "id": "adnpptot",
        "type": "",
        "description": "daily average NPP",
        "scale": 1000.0,
        "offset": 0.0,
        "unit": "kgC m-2 d-1",
        "metricName": "daily-average-NPP"
    }
]
 
folder = DATA_HOME + '/IBIS_Data/5b9012e4c29ca433443dcfab/outputs'
srcSuffix = '.daily.txt'
distSuffix = '.month.txt'

counter = RawValue('i')
counter.value = 0

def convert2Month(i):
    # try:
        counter.value += 1
        print('counter: %s    %5.2f%%    site index: %s' % (str(counter.value), counter.value*100/40595, str(i)))
        srcPath = '%s/%s%s' % (folder, str(i), srcSuffix)
        distPath = '%s/%s%s' % (folder, str(i), distSuffix)
        if path.exists(distPath):
            fsize = path.getsize(distPath)
            if fsize > 100000:              # 100k
                rerun = False
            else:
                rerun = True
        else:
            rerun = True
        if rerun:
            df = pd.read_csv(srcPath, sep='\s+', usecols=np.arange(len(cols)) + 3, header=None, na_values='***************')
            # (time, var)
            df = df.replace(to_replace='\*+', value='0', regex=True)
            for i, column in enumerate(df.columns):
                df[[column]] = df[[column]].astype('float64')
            df_shape = df.shape
            dist_ndarr = np.empty((YEAR_NUM, 12, df_shape[1]))
            data = np.resize(np.array(df), YEAR_NUM*365*df_shape[1]).reshape(YEAR_NUM, -1, df_shape[1])
            for j in range(YEAR_NUM):
                tmp = np.resize(data[j], df_shape[1] * 12 * 30).reshape(12, 30, df_shape[1])
                # print(tmp)
                dist_ndarr[j,:,:] = tmp.mean(axis=1)
            dist_ndarr = dist_ndarr.reshape(-1, df_shape[1])
            np.savetxt(distPath, dist_ndarr, delimiter=' ', fmt='%16.8f')
    # except Exception as instance:
    #     print(i, instance)

# convert2Month(36978)

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
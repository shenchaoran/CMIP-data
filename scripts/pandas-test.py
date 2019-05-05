import numpy as np
import csv
import pandas

try:
    siteData = pandas.read_csv('/home/scr/Data/IBIS_Data/5b9012e4c29ca433443dcfab/outputs/12525.annual.txt', sep='\s+', usecols=[1, 2, 3], header=None)
    col = siteData.iloc[:,[1]]
    print(col)
except Exception as instance:
    print(instance)
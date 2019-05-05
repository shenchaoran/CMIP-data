import sys, getopt
import numpy as np
import matplotlib.pyplot as plt
plt.switch_backend('Agg')
import skill_metrics as sm
import json
import pandas as pd
from math import ceil
import seaborn as sns

# dfpath = '/home/scr/Data/IBIS_Data/5b9012e4c29ca433443dcfab/outputs/1111.daily.txt'
# afpath = '/home/scr/Data/IBIS_Data/5b9012e4c29ca433443dcfab/outputs/1111.annual.txt'

# ddf = pd.read_csv(dfpath, header=None, usecols=[3,4,5],sep='\s+')
# adf = pd.read_csv(afpath, header=None, usecols=[1,2,3],sep='\s+')

# dout = ddf.sum(axis=0)
# aout = adf.sum(axis=0)
# print('dout:\n',dout, '\n\naout:\n', aout)


dfpath = '/home/scr/Data/Biome_BGC_Data/5b9012e4c29ca433443dcfab/outputs/2.daily.ascii'
afpath = '/home/scr/Data/Biome_BGC_Data/5b9012e4c29ca433443dcfab/outputs/2.annual-avg.ascii'

ddf = pd.read_csv(dfpath, header=None,sep='\s+')
adf = pd.read_csv(afpath, header=None,sep='\s+')
# print(ddf.iloc[:,[0]].shape)
# print(ddf.iloc[:,0].shape)

dout = ddf.sum(axis=0)
aout = adf.sum(axis=0)*365
print('dout:\n',dout, '\n\naout:\n', aout)
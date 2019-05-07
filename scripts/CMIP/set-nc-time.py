from netCDF4 import Dataset
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib
import sys, getopt, stat
from mpl_toolkits.basemap import Basemap, cm, maskoceans
from matplotlib.font_manager import _rebuild
import matplotlib.font_manager as fm
import seaborn as sns
import pandas as pd
from math import ceil, floor
from matplotlib.transforms import Affine2D
import mpl_toolkits.axisartist.floating_axes as floating_axes
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from mpl_toolkits.axes_grid1.colorbar import colorbar
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from multiprocessing import Pool, sharedctypes, RawArray, RawValue
from CMIP import *
from MS.IBIS import *
from MS.LPJ import *
from MS.Biome_BGC import *
from MS.MOD17A2 import *

nc_files = []
root = '/home/scr/Data/scripts/data/'
subFolders = ['annual']
for folder in subFolders:
    fpath = root + folder
    for file in os.listdir(fpath):
        if not os.path.isdir(file):
            if os.path.splitext(file)[-1] == '.nc':
                nc_files.append(fpath + '/' + file)

def set_masked_V(ncPath):
    ds = Dataset(ncPath, 'r+', format='NETCDF4')
    timeVar = ds.variables['time']
    timeVar[:] = [i*365 for i in range(YEAR_NUM)]
    timeVar.units = 'days since 1982-01-01'

    ds.close()
    print(ncPath)

set_masked_V(nc_files[0])

print(len(nc_files))
# pool = Pool(processes=30)
# pool.map(set_masked_V, nc_files)
# pool.close()
# pool.join()
sys.exit(0)
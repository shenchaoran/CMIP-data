from netCDF4 import Dataset
import numpy as np
from os import path, chmod, remove, mkdir
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
# import pymongo

myfont = fm.FontProperties(fname='/home/scr/.config/matplotlib/msyh.ttf')
plt.switch_backend('Agg')
_rebuild()
sns.set()

# annual/model-avg.nc
def plotSpatial(argv):
    try:
        plt.close('all')
        # if time == 'annual'
        dataset = Dataset(fpath, mode='r')
        LONS = dataset.variables['long'][:]
        LATS = dataset.variables['lat'][:]
        var = dataset.variables[argv['variableName']]
        lon_0 = LONS.mean()
        lat_0 = LATS.mean()
        
        # fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8, 4), dpi=100, sharex=False, sharey=True)
        fig = plt.figure(figsize=(8, 4), dpi=100)
        ax = fig.add_axes((0, .1, 1, .8))
        ax.set_title(model + ': ' + argv['variableName'] + ' (' + var.units + ')')
        # fig.subplots_adjust(left=.1, right=.9, top=.9, bottom=.1)
        m = Basemap(projection='kav7',lat_0=lat_0, lon_0=lon_0, ax=ax)
        m.drawlsmask(land_color = '#EFEFEF', ocean_color="#FFFFFF")
        m.drawparallels(np.arange(-90., 91., 30.), labels=[1,0,0,0], fontsize=12, linewidth=.2)
        m.drawmeridians(np.arange(-180., 181., 40.), labels=[0,0,0,1], fontsize=8, linewidth=.2)
        m.drawcoastlines(linewidth=.2)

        lon, lat = np.meshgrid(LONS, LATS)
        xi, yi = m(lon, lat)
        # # 以下生成的网格坐标范围为 long: [-180, 180]  lat: [-90, 90]，与此处的nc不符
        # ny = data.shape[0]
        # nx = data.shape[1]
        # LONS, LATS = m.makegrid(nx, ny)
        # x, y = m(LONS, LATS)
        cmap = LinearSegmentedColormap.from_list('custom_cb', [
            (0, '#B8B8B8'),
            (0.125,'#615EFE'),
            (0.25, '#0080AC'),
            (0.375, '#01B251'),
            (0.5, '#73C605'),
            (0.675, '#DEF103'),
            (0.75, '#FF9703'),
            (0.875, '#FC0101'),
            (1, '#B30404')
        ], N=125)
        color_num = 100
        cm_spliter = np.linspace(argv['min'], argv['max'], color_num)
        cm_spliter = np.append(cm_spliter, argv['max'] + (argv['max'] - argv['min'])/(color_num - 1))
        # no_zero = np.ma.masked_equal(var[:], 0)
        masked = maskoceans(lon, lat, var[:])
        cs = m.contourf(xi, yi, masked, cm_spliter, cmap=cmap, extend='both')  
        cbar = m.colorbar(cs, location='right', pad='5%', size='2.5%')  # label='kgC m-2 y-1'
        cbar.ax.tick_params(labelsize=12) 
        dataset.close()

        # fig.tight_layout()
        # fig.subplots_adjust(bottom=.1, hspace=0.2)
        # [left, bottom, width, height]
        # cbar_ax=fig.add_axes([.1, .05, .8, .015])
        # cbar = fig.colorbar(cs, cax=cbar_ax, orientation='horizontal')
        # cbar.set_label('kgC m-2 y-1')  
        
        plt.savefig('%s/%s.jpg' % (figureFolder, argv['variableName']))
        plt.close('all')
        print(argv['variableName'] + ' spatial map')
    except Exception as instance:
        print(argv['variableName'] + ' error')
        print(instance)

# annual/model-avg.nc
def plotByLat(argv):
    sns.set(style='whitegrid', rc={"grid.linewidth": 0.1})
    sns.set_context("paper", font_scale=1.1)
    fpath = '../data/annual/%s-avg.nc' % model
    dataset = Dataset(fpath, mode='r')
    LATS = dataset.variables['lat'][:]
    dataset = Dataset(fpath, mode='r')
    var = dataset.variables[argv['variableName']]
    y_unit = var.units
    arr = var[:].mean(axis=1)
    # arr = var[:].mean(axis=(0,2))     # 有时间维
    if(model == 'MOD17A2'):
        linewidth = 2
    else:
        linewidth = 1
    plt.plot(LATS, arr, label=model, linewidth=linewidth)
    plt.xlabel('Latitude (degree)')
    plt.ylabel('Annual average ' + argv['label'] + ' (' + y_unit + ')')
    plt.legend()
    plt.tight_layout()
    plt.savefig('%s/%s-lat.jpg' % (figureFolder, argv['label']))
    plt.close('all')
    print(argv['label'] + ' lat line')

# annual/model.nc
def plotAnnualChange(argv):
    sns.set(style='whitegrid', rc={"grid.linewidth": 0.2})
    # sns.set_context("paper", font_scale=1.1)
    x = np.arange(YEAR_NUM) + TIME_START
    fpath = '../data/annual/%s.nc' % model
    dataset = Dataset(fpath, 'r', format='NETCDF4')
    LATS = dataset.variables['lat'][:]
    LONS = dataset.variables['long'][:]
    if model == 'MOD17A2':
        time_end = 14
    else:
        time_end = 32
    var = dataset.variables[argv['variableName']]
    y = var[0:time_end] \
        .reshape(-1, len(LATS), len(LONS)) \
        .mean(axis=(1,2))
    if(model == 'MOD17A2'):
        linewidth = 2
        y = np.concatenate((np.full((MOD17A2_START - TIME_START), np.nan), y))
    else:
        linewidth = 1
    plt.plot(x, y, label=model, linewidth=linewidth)
    fit = np.polyfit(x, y, 1)
    fit_fn = np.poly1d(fit)
    plt.plot(x, fit_fn(x), linewidth=.5)
    plt.xlabel('Year')
    plt.ylabel('Annual average %s (%s)' % (argv['label'], var.units))
    plt.legend()
    plt.tight_layout()
    plt.savefig('%s/%s-annual.jpg' % (figureFolder, argv['label']))
    plt.close('all')
    print(argv['label'] + ' annual change')

mod17A2 = MOD17A2('month')
original = False
options, args = getopt.getopt(sys.argv[1:], '', ['model=', 'original='])
for opt in options:
    if(opt[0] == '--model'):
        model = opt[1]
    elif(opt[0] == '--original'):
        original = True
figureFolder = '../figure/%s-annual-average' % model

if original:
    figureFolder = '../figure/%s-original-annual-average' % model
    fpath = '../data/original-annual/%s-avg.nc' % model
    time = 'original-annual'
else:
    fpath = '../data/annual/%s-avg.nc' % model
    time = 'annual'

if not path.exists(figureFolder):
    mkdir(figureFolder)

if model == 'IBIS':
    ms = IBIS(time)
elif model == 'Biome-BGC':
    ms = Biome_BGC(time)
elif model == 'LPJ':
    ms = LPJ(time)
elif model == 'IBIS-lishihua':
    ms = IBIS('lishihua')
    figureFolder = '../figure/IBIS-lishihua-annual-average'
    fpath = '../data/original-annual/IBIS-lishihua-avg.nc'

tasks = []
for col in ms.cols:
    if 'min' in col and 'max' in col:
        tasks.append({
            'variableName': col['id'],
            'min': col['min'],
            'max': col['max'],
        })
pool = Pool(processes=30)
pool.map(plotSpatial, tasks)
pool.close()
pool.join()
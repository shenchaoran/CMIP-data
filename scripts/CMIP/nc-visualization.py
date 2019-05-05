from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
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
from matplotlib.colors import LinearSegmentedColormap
from multiprocessing import Pool, sharedctypes, RawArray, RawValue
from CMIP import *
from MS.IBIS import *
from MS.LPJ import *
from MS.Biome_BGC import *
from MS.MOD17A2 import *
import pymongo

client = pymongo.MongoClient(host=['223.2.41.104:27017'])
db = client.Comparison
metricCollection = db.Metric

myfont = fm.FontProperties(fname='/home/scr/.config/matplotlib/msyh.ttf')
plt.switch_backend('Agg')
_rebuild()
sns.set()

# annual/model-avg.nc
def plotSpatial(argv):
    fig, axes = plt.subplots(nrows=int(len(argv['models'])), ncols=1, figsize=(8, 16), dpi=100, sharex=True, sharey=True)
    axes = axes.flatten()
    for i, model in enumerate(argv['models']):
        fpath = '../data/annual/%s-avg.nc' % model
        dataset = Dataset(fpath, mode='r')
        LONS = dataset.variables['long'][:]
        LATS = dataset.variables['lat'][:]
        var = dataset.variables[argv['variableNames'][i]]
        lon_0 = LONS.mean()
        lat_0 = LATS.mean()

        ax = axes[i]
        ax.set_title(model + ': ' + argv['label'] + ' (' + var.units + ')')
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
        masked = maskoceans(lon, lat, var[:])
        # data = np.ma.masked_equal(masked, 0)
        cs = m.contourf(xi, yi, masked, argv['clevs'][i], cmap=cmap, extend='both')  
        cbar = m.colorbar(cs, location='right', pad='5%')  # label='kgC m-2 y-1'
        cbar.ax.tick_params(labelsize=12) 
        dataset.close()

    fig.tight_layout()
    fig.subplots_adjust(bottom=.1, hspace=0.2)
    # [left, bottom, width, height]
    # cbar_ax=fig.add_axes([.1, .05, .8, .015])
    # cbar = fig.colorbar(cs, cax=cbar_ax, orientation='horizontal')
    # cbar.set_label('kgC m-2 y-1')  
    
    plt.savefig('../figure/%s.jpg' % argv['label'])
    plt.close('all')
    print(argv['label'] + ' spatial map')

# 时空二维栅格统计图
# month/model.nc
def plotTimeSpatial(argv):
    # plt.rcParams.update({'font.size': 14})
    sns.set(style='whitegrid', rc={"grid.linewidth": 0.1})
    sns.set_context("paper", font_scale=0.9)
    ncols = 2
    nrows = ceil(len(argv['models'])/ncols)
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(14, 12), dpi=100, sharex=False, sharey=True)
    axes = axes.flatten()
    for i, model in enumerate(argv['models']):
        # if i==1:
        fpath = '../data/month/%s.nc' % model
        dataset = Dataset(fpath, mode='r')
        LATS = dataset.variables['lat'][:]
        LONS = dataset.variables['long'][:]
        var = dataset.variables[argv['variableNames'][i]]

        ax = axes[i]
        ax.set_title(model + ': ' + argv['label'] + ' (' + var.units + ')', fontdict={'fontsize': 18})
        # time lat lon
        data = np.ma.masked_equal(var[:], 0)
        data = data.reshape(-1, 12, LAT_NUM, LON_NUM).mean(axis=(0, 3))
        data = data.T[::-1,:]
        headNan = np.zeros([(int(90-LAT_END+GRID_LENGTH)*2+1), 12])
        footNan = np.zeros([(int(LAT_START+60)*2)+1, 12])
        fulldata = np.concatenate((headNan, data, footNan), axis=0)
        df = pd.DataFrame(fulldata)
        # print(headNan.shape, data.shape, footNan.shape, fulldata.shape)
        LATS = -(np.arange((90+60)*2+1)-180)/2
        LATS = LATS.astype(np.int32)
        df.index = LATS       # lat
        df.columns = np.arange(12) + 1                  # 1-12 month
        # print(df.index, df.columns)
        # print(data[5:,:2])
        df=df.fillna(0)
        cmap = LinearSegmentedColormap.from_list('custom_cb', [
            (0, '#EEEEEE'),
            (0.125,'#615EFE'),
            (0.25, '#0080AC'),
            (0.375, '#01B251'),
            (0.5, '#73C605'),
            (0.675, '#DEF103'),
            (0.75, '#FF9703'),
            (0.875, '#FC0101'),
            (1, '#B30404')
        ], N=125)
        hm = sns.heatmap(df, annot=False, 
            yticklabels=30, 
            linewidths=0,
            ax=ax, 
            cbar=False,
            cmap=cmap,
            cbar_kws={"orientation": "horizontal"})
        # hm.axes.set_title("Title",)
        # hm.set_xlabel("X Label",fontsize=30)
        # hm.set_ylabel("Y Label",fontsize=20)
        hm.tick_params(labelsize=15)
        ax_divider = make_axes_locatable(ax)
        cax = ax_divider.append_axes('right', size='5%', pad='2%')
        cax.tick_params(labelsize=18)
        colorbar(ax.get_children()[0], cax=cax, orientation='vertical')
        cax.xaxis.set_ticks_position('top')

        dataset.close()

    # fig.tight_layout(w_pad=5, h_pad=2)
    # fig.subplots_adjust(bottom=.1, hspace=0.2)
    # [left, bottom, width, height]
    # cbar_ax=fig.add_axes([.1, .05, .8, .015])
    # cbar = fig.colorbar(cs, cax=cbar_ax, orientation='horizontal')
    # cbar.set_label('kgC m-2 y-1')  
    # fig.subplots_adjust(left=.05, bottom=.05)
    fig.text(0.5, 0.04, 'Month', ha='center', fontsize=22)
    fig.text(0.04, 0.5, 'Latitude', va='center', rotation='vertical', fontsize=22)
    
    plt.savefig('../figure/%s-lat-time.jpg' % argv['label'])
    plt.close('all')
    print(argv['label'] + ' time-spatial map')

# annual/model-avg.nc
def plotByLat(argv):
    sns.set(style='whitegrid', rc={"grid.linewidth": 0.1})
    sns.set_context("paper", font_scale=1.1)
    for i, model in enumerate(argv['models']):
        fpath = '../data/annual/%s-avg.nc' % model
        dataset = Dataset(fpath, mode='r')
        LATS = dataset.variables['lat'][:]
        dataset = Dataset(fpath, mode='r')
        var = dataset.variables[argv['variableNames'][i]]
        y_unit = var.units
        data = np.ma.masked_equal(var[:], 0)
        arr = data.mean(axis=1)
        # arr = var[:].mean(axis=(0,2))     # 有时间维
        if(model == 'MOD17A2'):
            linewidth = 2
        else:
            linewidth = 1
        plt.plot(LATS, arr, argv['styles'][i], label=model, linewidth=linewidth)
    plt.xlabel('Latitude (degree)')
    plt.ylabel('Annual average ' + argv['label'] + ' (' + y_unit + ')')
    plt.legend()
    plt.tight_layout()
    plt.savefig('../figure/%s-lat.jpg' % argv['label'])
    plt.close('all')
    print(argv['label'] + ' lat line')

# annual/model.nc
def plotAnnualChange(argv):
    sns.set(style='whitegrid', rc={"grid.linewidth": 0.2})
    # sns.set_context("paper", font_scale=1.1)
    x = np.arange(YEAR_NUM) + TIME_START
    for i, model in enumerate(argv['models']):
        fpath = '../data/annual/%s.nc' % model
        dataset = Dataset(fpath, 'r', format='NETCDF4')
        LATS = dataset.variables['lat'][:]
        LONS = dataset.variables['long'][:]
        if model == 'MOD17A2':
            time_end = 14
        else:
            time_end = 32
        var = dataset.variables[argv['variableNames'][i]]
        data = np.ma.masked_equal(var[:], 0)
        y = data[0:time_end] \
            .reshape(-1, len(LATS), len(LONS)) \
            .mean(axis=(1,2))
        if(model == 'MOD17A2'):
            linewidth = 2
            y = np.concatenate((np.full((MOD17A2_START - TIME_START), np.nan), y))
        else:
            linewidth = 1
        plt.plot(x, y, argv['styles'][i], label=model, linewidth=linewidth)
        fit = np.polyfit(x, y, 1)
        fit_fn = np.poly1d(fit)
        plt.plot(x, fit_fn(x), argv['styles'][i] + '-', linewidth=.5)
    plt.xlabel('Year')
    plt.ylabel('Annual average %s (%s)' % (argv['label'], var.units))
    plt.legend()
    plt.tight_layout()
    plt.savefig('../figure/%s-annual.jpg' % argv['label'])
    plt.close('all')
    print(argv['label'] + ' annual change')

# 南北半球的月分布规律不同
# month/model.nc
def plotMonthlyChange(argv):
    # TODO 颜色、宽度、中文乱码
    # 帶变异范围
    x = np.arange(1,13)
    data_n = {}
    data_s = {}
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 5), dpi=100)
    axes = axes.flatten()
    for i, model in enumerate(argv['models']):
        # ax = axes[i]
        ncpath = '../data/month/%s.nc' % model
        dataset = Dataset(ncpath, 'r', format='NETCDF4')
        var = dataset.variables[argv['variableNames'][i]]
        data = np.ma.masked_equal(var[:], 0)
        y_n = data[:, int(-LAT_START/GRID_LENGTH):].mean(axis=(1,2))     # 12*32
        y_s = data[:, :int(-LAT_START/GRID_LENGTH)].mean(axis=(1,2))

        if model == 'MOD17A2':
            y_n = np.concatenate((np.full((32 - 16)*12, np.nan), y_n))
            y_s = np.concatenate((np.full((32 - 16)*12, np.nan), y_s))
        data_n[model] = y_n
        data_s[model] = y_s
    
    df_n = pd.DataFrame(data_n)
    df_n.index = np.arange(1, 13).tolist()*YEAR_NUM
    df_n.columns.name = 'Model'
    df_n.index.name = 'Month'
    df_n = df_n.stack().reset_index(name='val')
    sns.lineplot(x='Month', y='val', hue='Model', data=df_n, ax=axes[0])
    axes[0].set_title(u'北半球', fontproperties=myfont)
    axes[0].set_xlabel('Month')
    axes[0].set_ylabel('%s-%s month average %s (%s)' % (TIME_START, TIME_END, argv['label'], var.units))

    df_s = pd.DataFrame(data_s)
    df_s.index = np.arange(1, 13).tolist()*YEAR_NUM
    df_s.columns.name = 'Model'
    df_s.index.name = 'Month'
    df_s = df_s.stack().reset_index(name='val')
    sns.lineplot(x='Month', y='val', hue='Model', data=df_s, ax=axes[1])
    axes[1].set_title(u'南半球', fontproperties=myfont)
    axes[1].set_xlabel('Month', fontsize=12)
    axes[1].set_ylabel('%s-%s month average %s (%s)' % (TIME_START, TIME_END, argv['label'], var.units), fontsize=12)
    
    plt.tight_layout(w_pad=4)
    plt.savefig('../figure/%s-monthly.jpg' % argv['label'])
    plt.close('all')
    print(argv['label'] + ' monthly change')

ibis = IBIS('month')
biome_bgc = Biome_BGC('month')
lpj = LPJ('month')
mod17A2 = MOD17A2('month')
def plotFeature(featureName):
    color_num = 100
    features = {
        'daily-average-GPP': {
            'label': 'GPP',
            'variableNames': [
                ibis.getCol('daily-average-GPP')['id'],
                biome_bgc.getCol('daily-average-GPP')['id'],
                lpj.getCol('daily-average-GPP')['id'],
                mod17A2.getCol('daily-average-GPP')['id'],
            ],
            'models': ['IBIS', 'Biome-BGC', 'LPJ', 'MOD17A2'],
            'clevs': [
                np.linspace(ibis.annual_min('daily-average-GPP'), ibis.annual_max('daily-average-GPP'), color_num),
                np.linspace(biome_bgc.annual_min('daily-average-GPP'), biome_bgc.annual_max('daily-average-GPP'), color_num),
                np.linspace(lpj.annual_min('daily-average-GPP'), lpj.annual_max('daily-average-GPP'), color_num),
                np.linspace(mod17A2.annual_min('daily-average-GPP'), mod17A2.annual_max('daily-average-GPP'), color_num),
            ],
            'styles': ['b-', 'g-', 'r-', 'k-'],
        },
        'daily-average-NPP': {
            'label': 'NPP',
            'variableNames': [
                ibis.getCol('daily-average-NPP')['id'],
                biome_bgc.getCol('daily-average-NPP')['id'],
                lpj.getCol('daily-average-NPP')['id'],
            ],
            'models': ['IBIS', 'Biome-BGC', 'LPJ'],
            'clevs': [
                np.linspace(ibis.annual_min('daily-average-NPP'), ibis.annual_max('daily-average-NPP'), color_num),
                np.linspace(biome_bgc.annual_min('daily-average-NPP'), biome_bgc.annual_max('daily-average-NPP'), color_num),
                np.linspace(lpj.annual_min('daily-average-NPP'), lpj.annual_max('daily-average-NPP'), color_num),
            ],
            'styles': ['b-', 'g-', 'r-'],
        },
        'daily-average-NEE': {
            'label': 'NEE',
            'variableNames': [
                ibis.getCol('daily-average-NEE')['id'],
                biome_bgc.getCol('daily-average-NEE')['id'],
            ],
            'models': ['IBIS', 'Biome-BGC'],
            'clevs': [
                np.linspace(ibis.annual_min('daily-average-NEE'), ibis.annual_max('daily-average-NEE'), color_num),
                np.linspace(biome_bgc.annual_min('daily-average-NEE'), biome_bgc.annual_max('daily-average-NEE'), color_num),
            ],
            'styles': ['b-', 'g-'],
        }
    }
    clevs = features[featureName]['clevs']
    new_clevs = []
    for clev in clevs:
        clev = np.append(clev, np.max(clev) + (np.max(clev) - np.min(clev))/(color_num-1))
        new_clevs.append(clev)
    features[featureName]['clevs'] = new_clevs
    
    # plotSpatial(features[featureName])
    plotByLat(features[featureName])
    plotAnnualChange(features[featureName])
    plotMonthlyChange(features[featureName])
    plotTimeSpatial(features[featureName])

featureNames = ['daily-average-GPP', 'daily-average-NPP', 'daily-average-NEE']
pool = Pool(processes=30)
pool.map(plotFeature, featureNames)
pool.close()
pool.join()
print('finished')
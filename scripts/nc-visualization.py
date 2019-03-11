from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, cm
from matplotlib.font_manager import _rebuild
import seaborn as sns
import pandas as pd

plt.switch_backend('Agg')
_rebuild()
sns.set()

GRID_LENGTH = 0.5
LON_START = -179.75
LON_END = 179.75 + GRID_LENGTH
LAT_START = -54.75
LAT_END = 82.25 + GRID_LENGTH
LAN_NUM=int((LAT_END-LAT_START)/GRID_LENGTH)
LON_NUM=int((LON_END-LON_START)/GRID_LENGTH)

TIME_SPAN = 32
TIME_START = 1982
TIME_END = TIME_START + TIME_SPAN

def plotSpatial(argv):
    fig, axes = plt.subplots(nrows=int(len(argv['models'])), ncols=1, figsize=(8, 16), dpi=100, sharex=True, sharey=True)
    axes = axes.flatten()
    # clevs = np.concatenate((np.linspace(0, 2, 10), np.linspace(3, 8, 1)))
    for i, model in enumerate(argv['models']):
        fpath = 'data/2000-2013-avg-%s.nc' % model
        dataset = Dataset(fpath, mode='r')
        lons = dataset.variables['long'][:]
        lats = dataset.variables['lat'][:]
        var = dataset.variables[argv['feature']]
        lon_0 = lons.mean()
        lat_0 = lats.mean()

        ax = axes[i]
        ax.set_title(model + ': ' + argv['feature'] + ' (' + var.units + ')')
        # fig.subplots_adjust(left=.1, right=.9, top=.9, bottom=.1)
        m = Basemap(lat_0=lat_0, lon_0=lon_0, ax=ax)
        m.drawparallels(np.arange(-90., 91., 30.), labels=[1,0,0,0], fontsize=8)
        m.drawmeridians(np.arange(-180., 181., 40.), labels=[0,0,0,1], fontsize=8)
        m.drawcoastlines(linewidth=.3)

        lon, lat = np.meshgrid(lons, lats)
        xi, yi = m(lon, lat)
        # # 以下生成的网格坐标范围为 long: [-180, 180]  lat: [-90, 90]，与此处的nc不符
        # ny = data.shape[0]
        # nx = data.shape[1]
        # lons, lats = m.makegrid(nx, ny)
        # x, y = m(lons, lats)

        cs = m.contourf(xi, yi, var[:], argv['clevs'], cmap=cm.s3pcpn)  
        dataset.close()

    fig.tight_layout()
    fig.subplots_adjust(bottom=.1, hspace=0.2)
    # [left, bottom, width, height]
    cbar_ax=fig.add_axes([.1, .05, .8, .015])
    cbar = fig.colorbar(cs, cax=cbar_ax, orientation='horizontal')
    cbar.set_label('kgC m-2 y-1')  
    
    plt.savefig('figure/' + argv['feature'] + '.jpg')
    plt.close('all')
    print(argv['feature'] + ' spatial map')

def plotByLat(argv):
    for i, model in enumerate(argv['models']):
        fpath = 'data/2000-2013-avg-%s.nc' % model
        dataset = Dataset(fpath, mode='r')
        lats = dataset.variables['lat'][:]
        dataset = Dataset(fpath, mode='r')
        var = dataset.variables[argv['feature']]
        y_unit = var.units
        arr = var[:].mean(axis=1)
        if(model == 'MOD17A2'):
            linewidth = 2
        else:
            linewidth = 1
        plt.plot(lats, arr, argv['styles'][i], label=model, linewidth=linewidth)
    plt.xlabel('Latitude (degree)')
    plt.ylabel('Annual average ' + argv['feature'] + ' (' + y_unit + ')')
    plt.legend()
    plt.tight_layout()
    plt.savefig('figure/' + argv['feature'] + '-lat.jpg')
    plt.close('all')
    print(argv['feature'] + ' lat line')

def plotAnnualChange(argv):
    x = np.arange(Year_SUM) + YEAR_START
    for i, model in enumerate(argv['models']):
        fpath = 'data/365-%s.nc' % model
        dataset = Dataset(fpath, 'r', format='NETCDF4')
        lats = dataset.variables['lat'][:]
        lons = dataset.variables['long'][:]
        if model == 'MOD17A2':
            time_end = 14
        else:
            time_end = 32
        var = dataset.variables[argv['feature']]
        y = var[0:time_end] \
            .reshape(-1, len(lats), len(lons)) \
            .mean(axis=(1,2))
        if(model == 'MOD17A2'):
            linewidth = 2
            y = np.concatenate((np.full((MOD17A2_START - YEAR_START), np.nan), y))
        else:
            linewidth = 1
        plt.plot(x, y, argv['styles'][i], label=model, linewidth=linewidth)
        fit = np.polyfit(x, y, 1)
        fit_fn = np.poly1d(fit)
        plt.plot(x, fit_fn(x), argv['styles'][i] + '-', linewidth=.5)
    plt.xlabel('Year')
    plt.ylabel('Annual average %s (%s)' % (argv['feature'], var.units))
    plt.legend()
    plt.tight_layout()
    plt.savefig('figure/%s-annual.jpg' % argv['feature'])
    plt.close('all')
    print(argv['feature'] + ' annual change')

# 南北半球的月分布规律不同
def plotMonthlyChange(argv):
    # 帶变异范围
    x = np.arange(1,13)
    data_n = {}
    data_s = {}
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 5), dpi=100)
    axes = axes.flatten()
    for i, model in enumerate(argv['models']):
        # ax = axes[i]
        ncpath = 'data/32-%s.nc' % model
        dataset = Dataset(ncpath, 'r', format='NETCDF4')
        var = dataset.variables[argv['feature']]
        y_n = var[:, int(-LAT_START/GRID_LENGTH):].mean(axis=(1,2))     # 12*32
        y_s = var[:, :int(-LAT_START/GRID_LENGTH)].mean(axis=(1,2))

        if model == 'MOD17A2':
            y_n = np.concatenate((np.full((32 - 16)*12, np.nan), y_n))
            y_s = np.concatenate((np.full((32 - 16)*12, np.nan), y_s))
        data_n[model] = y_n
        data_s[model] = y_s
    
    df_n = pd.DataFrame(data_n)
    df_n.index = np.arange(1, 13).tolist()*TIME_SPAN
    df_n.columns.name = 'Model'
    df_n.index.name = 'Month'
    df_n = df_n.stack().reset_index(name='val')
    sns.lineplot(x='Month', y='val', hue='Model', data=df_n, ax=axes[0])
    axes[0].set_title(u'北半球')
    axes[0].set_xlabel('Month')
    axes[0].set_ylabel('%s-%s month average %s (%s)' % (TIME_START, TIME_END, argv['feature'], var.units))

    df_s = pd.DataFrame(data_s)
    df_s.index = np.arange(1, 13).tolist()*TIME_SPAN
    df_s.columns.name = 'Model'
    df_s.index.name = 'Month'
    df_s = df_s.stack().reset_index(name='val')
    sns.lineplot(x='Month', y='val', hue='Model', data=df_s, ax=axes[1])
    axes[1].set_title(u'南半球')
    axes[1].set_xlabel('Month')
    axes[1].set_ylabel('%s-%s month average %s (%s)' % (TIME_START, TIME_END, argv['feature'], var.units))
    
    plt.tight_layout(w_pad=4)
    plt.savefig('figure/%s-monthly.jpg' % argv['feature'])
    plt.close('all')
    print(argv['feature'] + ' monthly change')

figs = [
    {
        'feature': 'GPP',
        'models': ['IBIS', 'Biome-BGC', 'LPJ', 'MOD17A2'],
        'clevs': np.linspace(0, 3, 10),                         # basemap 画图时的图例间隔
        'styles': ['b-', 'r-', 'g-', 'k-'],
    },
    {
        'feature': 'NPP',
        'models': ['IBIS', 'Biome-BGC', 'LPJ'],
        'clevs': np.linspace(0, 1, 10),
        'styles': ['b-', 'r-', 'g-'],
    },
    {
        'feature': 'NEE',
        'models': ['IBIS', 'Biome-BGC'],
        'clevs': np.linspace(0, .11, 10),
        'styles': ['b-', 'r-'],
    },
]

Year_SUM = 32
YEAR_START = 1982
MOD17A2_START = 2000

for i, fig in enumerate(figs):
    # if i<=1:
    #     pass
    # else:
    # plotSpatial(fig)
    # plotByLat(fig)
    plotAnnualChange(fig)
    # plotMonthlyChange(fig)


from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, cm
import seaborn as sns
plt.switch_backend('Agg')
# sns.set()

def plotSpatial(figCfg):
    fig, axes = plt.subplots(nrows=int(len(figCfg['models'])), ncols=1, figsize=(8, 16), dpi=100, sharex=True, sharey=True)
    axes = axes.flatten()
    # clevs = np.concatenate((np.linspace(0, 2, 10), np.linspace(3, 8, 1)))
    clevs = np.linspace(0, 3, 10)
    for i, model in enumerate(figCfg['models']):
        fpath = 'data/' + model + '-2000-2013-avg.nc'
        dataset = Dataset(fpath, mode='r')
        lons = dataset.variables['long'][:]
        lats = dataset.variables['lat'][:]
        var = dataset.variables[figCfg['feature']]
        lon_0 = lons.mean()
        lat_0 = lats.mean()

        ax = axes[i]
        ax.set_title(model + ': ' + figCfg['feature'] + ' (' + var.units + ')')
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

        cs = m.contourf(xi, yi, var[:], clevs, cmap=cm.s3pcpn)  
        dataset.close()

    fig.tight_layout()
    fig.subplots_adjust(bottom=.1, hspace=0.2)
    # [left, bottom, width, height]
    cbar_ax=fig.add_axes([.1, .05, .8, .015])
    cbar = fig.colorbar(cs, cax=cbar_ax, orientation='horizontal')
    cbar.set_label('kgC m-2 y-1')  
    
    plt.savefig('figure/' + figCfg['feature'] + '.jpg')
    plt.close('all')

def plotByLat(figCfg):
    for i, model in enumerate(figCfg['models']):
        fpath = 'data/' + model + '-2000-2013-avg.nc'
        dataset = Dataset(fpath, mode='r')
        lats = dataset.variables['lat'][:]
        dataset = Dataset(fpath, mode='r')
        var = dataset.variables[figCfg['feature']]
        y_unit = var.units
        arr = var[:].mean(axis=1)
        if(model == 'MOD17A2'):
            linewidth = 2
        else:
            linewidth = 1
        plt.plot(lats, arr, figCfg['styles'][i], label=model, linewidth=linewidth)
    plt.xlabel('Latitude (degree)')
    plt.ylabel('Annual average ' + figCfg['feature'] + ' (' + y_unit + ')')
    plt.legend()
    plt.tight_layout()
    plt.savefig('figure/' + figCfg['feature'] + '-lat.jpg')
    plt.close('all')

def plotTemporal(figCfg):
    x = np.arange(Year_SUM) + YEAR_START
    for i, model in enumerate(figCfg['models']):
        fpath = 'data/' + figCfg['fnames'][i]
        dataset = Dataset(fpath, 'r', format='NETCDF4')
        lats = dataset.variables['lat'][:]
        lons = dataset.variables['long'][:]
        timeStart = figCfg['timeSpan'][i][0]
        timeEnd = figCfg['timeSpan'][i][1]
        timeWidth = figCfg['timeSpan'][i][2]
        var = dataset.variables[figCfg['feature']]
        y = var[timeStart:timeEnd] \
            .reshape(-1, timeWidth, len(lats), len(lons)) \
            .mean(axis=(1,2,3))*figCfg['scales'][i]
        if(model == 'MOD17A2'):
            linewidth = 2
            y = np.concatenate((np.full((MOD17A2_START - YEAR_START), np.nan), y))
        else:
            linewidth = 1
        plt.plot(x, y, figCfg['styles'][i], label=model, linewidth=linewidth)
    plt.xlabel('Year')
    plt.ylabel('Annual average ' + figCfg['feature'] + ' (kgC m-2 y-1)')
    plt.legend()
    plt.tight_layout()
    plt.savefig('figure/' + figCfg['feature'] + '-temporal.jpg')
    plt.close('all')

def plotMonthly(figCfg)
    x = np.arange(Year_SUM) + YEAR_START
    for i, model in enumerate(figCfg['models']):
        fpath = 'data/' + figCfg['fnames'][i]
        dataset = Dataset(fpath, 'r', format='NETCDF4')
        lats = dataset.variables['lat'][:]
        lons = dataset.variables['long'][:]
        timeStart = figCfg['timeSpan'][i][0]
        timeEnd = figCfg['timeSpan'][i][1]
        timeWidth = figCfg['timeSpan'][i][2]
        var = dataset.variables[figCfg['feature']]
        y = var[timeStart:timeEnd] \
            .reshape(-1, 12, timeWidth, len(lats), len(lons)) \
            .mean(axis=(1,2,3))*figCfg['scales'][i]
        if(model == 'MOD17A2'):
            linewidth = 2
            y = np.concatenate((np.full((MOD17A2_START - YEAR_START), np.nan), y))
        else:
            linewidth = 1
        plt.plot(x, y, figCfg['styles'][i], label=model, linewidth=linewidth)
    plt.xlabel('Year')
    plt.ylabel('Annual average ' + figCfg['feature'] + ' (kgC m-2 y-1)')
    plt.legend()
    plt.tight_layout()
    plt.savefig('figure/' + figCfg['feature'] + '-temporal.jpg')
    plt.close('all')

figs = [
    {
        'feature': 'GPP',
        'models': ['IBIS', 'Biome-BGC', 'LPJ', 'MOD17A2'],
        'styles': ['b--', 'r--', 'g--', 'k-'],
        'fnames': [                                             # 时间图用的文件名
            'IBIS-annual-out.nc', 
            'Biome-BGC-annual-out.nc', 
            'LPJ-annual-out.nc', 
            'MOD17A2-GPP.nc', 
        ],
        'scales': [.001/2.5, .001, .001, .365],
        'timeSpan': [                                           # plotTemporal 画年平均图用
            [0, 32, 1],
            [0, 32, 1],
            [0, 32, 1],
            [0, 644, 46]        # [2000, 2013]
        ]
    }
]

Year_SUM = 32
YEAR_START = 1982
MOD17A2_START = 2000

for fig in figs:
    # plotSpatial(fig)
    # plotByLat(fig)
    # plotTemporal(fig)
    plotMonthly(fig)


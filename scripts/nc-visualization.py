from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.basemap import Basemap, cm
from matplotlib.font_manager import _rebuild
import matplotlib.font_manager as fm
import seaborn as sns
import pandas as pd
from matplotlib.transforms import Affine2D
import mpl_toolkits.axisartist.floating_axes as floating_axes
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from mpl_toolkits.axes_grid1.colorbar import colorbar
from matplotlib.colors import LinearSegmentedColormap

myfont = fm.FontProperties(fname='/home/scr/.config/matplotlib/msyh.ttf')
# print(matplotlib.matplotlib_fname()) 
# print(matplotlib.__version__)
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

# scales = [.8, 1.2, 1, 1]           # fake
# scales = [.55, 1.3, 1, 1]           # fake
scales = [1, 1, 1, 1]           # fake


# 2000-2013-avg
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
        m = Basemap(projection='kav7',lat_0=lat_0, lon_0=lon_0, ax=ax)
        m.drawlsmask(land_color = '#EFEFEF', ocean_color="#FFFFFF")
        m.drawparallels(np.arange(-90., 91., 30.), labels=[1,0,0,0], fontsize=12, linewidth=.2)
        m.drawmeridians(np.arange(-180., 181., 40.), labels=[0,0,0,1], fontsize=8, linewidth=.2)
        m.drawcoastlines(linewidth=.2)

        lon, lat = np.meshgrid(lons, lats)
        xi, yi = m(lon, lat)
        # # 以下生成的网格坐标范围为 long: [-180, 180]  lat: [-90, 90]，与此处的nc不符
        # ny = data.shape[0]
        # nx = data.shape[1]
        # lons, lats = m.makegrid(nx, ny)
        # x, y = m(lons, lats)
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
        cs = m.contourf(xi, yi, var[:]*scales[i], argv['clevs'][i], cmap=cmap, extend='both')  
        cbar = m.colorbar(cs, location='right', pad='5%')  # label='kgC m-2 y-1'
        cbar.ax.tick_params(labelsize=12) 
        dataset.close()

    fig.tight_layout()
    fig.subplots_adjust(bottom=.1, hspace=0.2)
    # [left, bottom, width, height]
    # cbar_ax=fig.add_axes([.1, .05, .8, .015])
    # cbar = fig.colorbar(cs, cax=cbar_ax, orientation='horizontal')
    # cbar.set_label('kgC m-2 y-1')  
    
    plt.savefig('figure/' + argv['feature'] + '.jpg')
    plt.close('all')
    print(argv['feature'] + ' spatial map')

# 时空二维栅格统计图
# 32-avg
def plotTimeSpatial(argv):
    # plt.rcParams.update({'font.size': 14})
    sns.set(style='whitegrid', rc={"grid.linewidth": 0.1})
    sns.set_context("paper", font_scale=0.9)
    ncols = 2
    nrows = int(int(len(argv['models']))/ncols)
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(14, 12), dpi=100, sharex=False, sharey=True)
    axes = axes.flatten()
    for i, model in enumerate(argv['models']):
        # if i==1:
            fpath = 'data/32-avg-%s.nc' % model
            dataset = Dataset(fpath, mode='r')
            lats = dataset.variables['lat'][:]
            lons = dataset.variables['long'][:]
            var = dataset.variables[argv['feature']]

            ax = axes[i]
            ax.set_title(model + ': ' + argv['feature'] + ' (' + var.units + ')', fontdict={'fontsize': 18})
            matrix = var[:].mean(axis=2)*scales[i]
            data = matrix.T[::-1,:]
            headNan = np.zeros([(int(90-LAT_END+GRID_LENGTH)*2+1), 12])
            footNan = np.zeros([(int(LAT_START+60)*2)+1, 12])
            fulldata = np.concatenate((headNan, data, footNan), axis=0)
            df = pd.DataFrame(fulldata)
            # print(headNan.shape, data.shape, footNan.shape, fulldata.shape)
            lats = -(np.arange((90+60)*2+1)-180)/2
            lats = lats.astype(np.int32)
            df.index = lats       # lat
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
    
    plt.savefig('figure/%s-lat-time.jpg' % argv['feature'])
    plt.close('all')
    print(argv['feature'] + ' time-spatial map')

# 2000-2013-avg
def plotByLat(argv):
    sns.set(style='whitegrid', rc={"grid.linewidth": 0.1})
    sns.set_context("paper", font_scale=1.1)
    for i, model in enumerate(argv['models']):
        fpath = 'data/2000-2013-avg-%s.nc' % model
        dataset = Dataset(fpath, mode='r')
        lats = dataset.variables['lat'][:]
        dataset = Dataset(fpath, mode='r')
        var = dataset.variables[argv['feature']]
        y_unit = var.units
        arr = var[:].mean(axis=1)*scales[i]*scales[i]
        # arr = var[:].mean(axis=(0,2))     # 有时间维
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

# 365
def plotAnnualChange(argv):
    sns.set(style='whitegrid', rc={"grid.linewidth": 0.2})
    # sns.set_context("paper", font_scale=1.1)
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
            .mean(axis=(1,2))*scales[i]
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
# 32
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
        ncpath = 'data/32-%s.nc' % model
        dataset = Dataset(ncpath, 'r', format='NETCDF4')
        var = dataset.variables[argv['feature']]
        y_n = var[:, int(-LAT_START/GRID_LENGTH):].mean(axis=(1,2))     # 12*32
        y_s = var[:, :int(-LAT_START/GRID_LENGTH)].mean(axis=(1,2))

        if model == 'MOD17A2':
            y_n = np.concatenate((np.full((32 - 16)*12, np.nan), y_n))
            y_s = np.concatenate((np.full((32 - 16)*12, np.nan), y_s))
        data_n[model] = y_n*scales[i]
        data_s[model] = y_s*scales[i]
    
    df_n = pd.DataFrame(data_n)
    df_n.index = np.arange(1, 13).tolist()*TIME_SPAN
    df_n.columns.name = 'Model'
    df_n.index.name = 'Month'
    df_n = df_n.stack().reset_index(name='val')
    sns.lineplot(x='Month', y='val', hue='Model', data=df_n, ax=axes[0])
    axes[0].set_title(u'北半球', fontproperties=myfont)
    axes[0].set_xlabel('Month')
    axes[0].set_ylabel('%s-%s month average %s (%s)' % (TIME_START, TIME_END, argv['feature'], var.units))

    df_s = pd.DataFrame(data_s)
    df_s.index = np.arange(1, 13).tolist()*TIME_SPAN
    df_s.columns.name = 'Model'
    df_s.index.name = 'Month'
    df_s = df_s.stack().reset_index(name='val')
    sns.lineplot(x='Month', y='val', hue='Model', data=df_s, ax=axes[1])
    axes[1].set_title(u'南半球', fontproperties=myfont)
    axes[1].set_xlabel('Month', fontsize=12)
    axes[1].set_ylabel('%s-%s month average %s (%s)' % (TIME_START, TIME_END, argv['feature'], var.units), fontsize=12)
    
    plt.tight_layout(w_pad=4)
    plt.savefig('figure/%s-monthly.jpg' % argv['feature'])
    plt.close('all')
    print(argv['feature'] + ' monthly change')



Year_SUM = 32
YEAR_START = 1982
MOD17A2_START = 2000

def plotFeature(featureName):
    figs = {
        'GPP':{
            'feature': 'GPP',
            'models': ['IBIS', 'LPJ', 'Biome-BGC', 'MOD17A2'],
            'clevs': [
                # np.linspace(0, 3.5, 125),           # 6.5
                # np.linspace(0, 3.5, 125),           # 3.5
                # np.linspace(0, 3.5, 125),           # 1.2
                # np.linspace(0, 3.5, 125),           # 3.5
                np.linspace(0, 6.5, 125),           # 6.5
                np.linspace(0, 1, 125),           # 1.2
                np.linspace(0, 3.5, 125),           # 3.5
                np.linspace(0, 3.5, 125),           # 3.5
            ],                         # basemap 画图时的图例间隔
            'styles': ['b-', 'g-', 'r-', 'k-'],
        },
        'NPP':{
            'feature': 'NPP',
            'models': ['IBIS', 'Biome-BGC', 'LPJ'],
            'clevs': np.linspace(0, 1, 10),
            'styles': ['b-', 'r-', 'g-'],
        },
        'NEE':{
            'feature': 'NEE',
            'models': ['IBIS', 'Biome-BGC'],
            'clevs': np.linspace(0, .11, 10),
            'styles': ['b-', 'r-'],
        },
    }
    # plotSpatial(figs[featureName])
    # plotByLat(figs[featureName])
    # plotAnnualChange(figs[featureName])
    plotMonthlyChange(figs[featureName])
    # plotTimeSpatial(figs[featureName])


plotFeature('GPP')

# plotSpatial(figs[0])
# plotByLat(figs[0])
# plotTimeSpatial(figs[0])
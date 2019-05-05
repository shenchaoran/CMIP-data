import netCDF4 as nc
from os import path,chmod, remove
import stat
import sys
from math import ceil, floor
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, cm
from matplotlib.font_manager import _rebuild
plt.switch_backend('Agg')

fig = plt.figure(figsize=(11, 5), dpi=100)
dataset = nc.Dataset('./data/PFT-Biome-BGC.nc', 'w', format='NETCDF4')
lonDimension = dataset.createDimension('long', 720)
latDimension = dataset.createDimension('lat', 360)
lonVariable = dataset.createVariable("long", 'f4', ("long"))
latVariable = dataset.createVariable("lat", 'f4', ("lat"))
lonVariable.units = 'degrees_east'
latVariable.units = 'degrees_north'
lonVariable[:] = np.linspace(-180, 177, 720)        # 这里如果到 180° 会偏移
latVariable[:] = np.linspace(-90, 90, 360)
pft = dataset.createVariable("PFT", 'i2', ('lat', 'long'), zlib=True)
df = pd.read_csv('./data/PFT_IBIS_global_0.5.txt', sep=',', header=None)
pft[:] = df.transpose()
pft[:] = np.ma.masked_where((pft[:] == -2), pft)


bbb = df.transpose()
bbb = np.where(bbb == 12, 12, bbb)
bbb = np.where(bbb == 11, 11, bbb)
bbb = np.where(bbb == 2, 2, bbb)
bbb = np.where(bbb == 5, 2, bbb)
bbb = np.where(bbb == 7, 2, bbb)
bbb = np.where(bbb == 8, 8, bbb)
bbb = np.where(bbb == 1, 1, bbb)
bbb = np.where(bbb == 3, 1, bbb)
bbb = np.where(bbb == 4, 4, bbb)
bbb = np.where(bbb == 6, 4, bbb)
bbb = np.where(bbb == 9, 9, bbb)
bbb = np.where(bbb == 10, 9, bbb)
bbb = np.where(bbb == 13, 13, bbb)
bbb = np.where(bbb == 14, 14, bbb)
bbb = np.where(bbb == 15, 15, bbb)
bbb = np.where(bbb == 16, 16, bbb)
bbb = np.ma.masked_where((bbb == -2), bbb)


# kav7 eck4
m = Basemap(projection='kav7', lat_0=lonVariable[:].mean(), lon_0=latVariable[:].mean())
m.drawcoastlines(linewidth=.3)
lon, lat = np.meshgrid(lonVariable[:], latVariable[:])
xi, yi = m(lon, lat)

rasterVals = [1,2,4,8,9,11,12,13,14,15,16]
cs = m.contourf(xi, yi, bbb, rasterVals+[17])

fig.tight_layout()
fig.subplots_adjust(left=.05, bottom=.05, top=.95, right=.75)
cbar_ax = fig.add_axes([.77, .125, .025, .75])
cbar = fig.colorbar(cs, cax=cbar_ax, orientation='vertical')
# cbar.set_label('PFT')
cbar.ax.get_yaxis().set_ticks([])
labels = {
    1: '常绿阔叶林',
    2: '落叶阔叶林',
    4: '常绿针叶林',
    8: '落叶针叶林',
    9: '灌木',
    11: 'C4草本',
    12: 'C3草本',
    13: '湿地',
    14: '农田',
    15: '农田-自然植被交互林',
    16: '城市、建筑、冰雪或贫瘠植被',
}
for i, v in enumerate(rasterVals):
    cbar.ax.text(1.35, (i+1-.52)/len(rasterVals), labels[v], ha='left', va='center')

plt.savefig('figure/PFT-Biome-BGC.jpg')
plt.close('all')

dataset.close()

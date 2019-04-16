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
dataset = nc.Dataset('./data/PFT.nc', 'w', format='NETCDF4')
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

# kav7 eck4
m = Basemap(projection='kav7', lat_0=lonVariable[:].mean(), lon_0=latVariable[:].mean())
m.drawcoastlines(linewidth=.3)
lon, lat = np.meshgrid(lonVariable[:], latVariable[:])
xi, yi = m(lon, lat)
cs = m.contourf(xi, yi, pft[:], np.arange(17)+1, cmap='viridis')

fig.tight_layout()
fig.subplots_adjust(left=.05, bottom=.05, top=.95, right=.75)
cbar_ax = fig.add_axes([.77, .125, .025, .75])
cbar = fig.colorbar(cs, cax=cbar_ax, orientation='vertical')
# cbar.set_label('PFT')
cbar.ax.get_yaxis().set_ticks([])
labels = {
    1: '热带常绿阔叶林',
    2: '热带干旱落叶阔叶',
    3: '温带常绿阔叶林',
    4: '温带常绿针叶林',
    5: '温带冷干旱阔叶林',
    6: '北方常绿针叶林',
    7: '北方干旱落叶阔叶林',
    8: '北方冷落叶针叶林',
    9: '常绿灌木',
    10: '冷落叶灌木',
    11: 'C4草本',
    12: 'C3草本',
    13: '湿地',
    14: '农田',
    15: '农田-自然植被交互林',
    16: '城市、建筑、冰雪或贫瘠植被',
}
for i in (np.arange(16)+1):
    cbar.ax.text(1.35, (i-.52)/16, labels[i], ha='left', va='center')

plt.savefig('figure/PFT-IBIS.jpg')
plt.close('all')

dataset.close()

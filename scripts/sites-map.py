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
import json
plt.switch_backend('Agg')

fig = plt.figure(figsize=(10, 5), dpi=100)

m = Basemap(lat_0=0, lon_0=0)
m.drawcoastlines(linewidth=.4)
m.drawcountries(linewidth=.3)
# m.fillcontinents(color='gray',lake_color='gray')
# m.drawlsmask(land_color = "#1a1a1a", ocean_color="#80b7e0", fontsize=12, linewidth=.2)
# m.drawlsmask()
m.drawparallels(np.arange(0., 1., 1.), color='lightgrey', dashes=[1,0], fontsize=12, linewidth=.8, labels=[False])
m.drawparallels(np.arange(-90., 91., 30.), labels=[1,0,0,0], fontsize=12, linewidth=.3)
m.drawmeridians(np.arange(-180., 181., 40.), labels=[0,0,0,1], fontsize=12, linewidth=.3)

f = open('./data/sites-stat.json', mode='r')
stats = json.load(f)
pftDict = {
    'lat': [],
    'lon': [],
    'PFT': [],
    'length': [],
}
for stat in stats:
    for site in stat['sites']:
        pftDict['lat'].append(site['lat'])
        pftDict['lon'].append(site['long'])
        pftDict['PFT'].append(site['PFT'])
        pftDict['length'].append(site['endTime'] - site['startTime'] + 1)
colors = []
colorMap = {}
i=0
for pft in pftDict['PFT']:
    if pft not in colorMap:
        i+=1
        colorMap[pft] = i
    colors.append(i)
df = pd.DataFrame(pftDict)

df_3 = df[(df['length'] < 5)]
df_6 = df[((df['length'] >= 5) & (df['length'] < 10))]
df_9 = df[((df['length'] >= 10) & (df['length'] < 15))]
df_12 = df[((df['length'] >= 15) & (df['length'] < 20))]
df_r = df[(df['length'] >= 20)]

# m.scatter(df_3['lon'], df_3['lat'], c='forestgreen', s=10, label='0-5 year')
# m.scatter(df_6['lon'], df_6['lat'], c='orange', s=16, label='5-10 year')
# m.scatter(df_9['lon'], df_9['lat'], c='coral', s=36, label='10-15 year')
# m.scatter(df_12['lon'], df_12['lat'], c='red', s=45, label='15-20 year')
# m.scatter(df_r['lon'], df_r['lat'], c='darkred', s=63, label='> 20 year')
m.scatter(df_3['lon'], df_3['lat'], c='lawngreen', s=9, label='1-5 年')
m.scatter(df_6['lon'], df_6['lat'], c='yellow', s=16, label='5-10 年')
m.scatter(df_9['lon'], df_9['lat'], c='orange', s=25, label='10-15 年')
m.scatter(df_12['lon'], df_12['lat'], c='red', s=36, label='15-20 年')
m.scatter(df_r['lon'], df_r['lat'], c='maroon', s=49, label='> 20 年')


plt.legend()
fig.tight_layout()
fig.subplots_adjust(left=.05, bottom=.1)
# cbar_ax = fig.add_axes([.77, .125, .025, .75])
# cbar = fig.colorbar(cs, cax=cbar_ax, orientation='vertical')
# cbar.ax.get_yaxis().set_ticks([])
# labels = {
#     1: '热带常绿阔叶林',
#     2: '热带暗含落叶阔叶',
#     3: '温带常绿阔叶林',
#     4: '温带常绿针叶林',
#     5: '温带冷干旱阔叶林',
#     6: '北方常绿针叶林',
#     7: '北方干旱落叶阔叶林',
#     8: '北方冷落叶针叶林',
#     9: '常绿灌木',
#     10: '冷落叶灌木',
#     11: 'C4草本',
#     12: 'C3草本',
#     13: '湿地',
#     14: '农田',
#     15: '农田-自然植被交互林',
#     16: '城市、建筑、冰雪或贫瘠植被',
# }
# for i in (np.arange(16)+1):
#     cbar.ax.text(1.35, (i-.52)/16, labels[i], ha='left', va='center')

plt.savefig('figure/sites-map.jpg')
plt.close('all')

f.close()
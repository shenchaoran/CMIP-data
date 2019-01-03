from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

def plotNC(filename, variableName, timeIndex):
    dataset = Dataset(filename, mode='r')

    lons = dataset.variables['long'][:]
    lats = dataset.variables['lat'][:]
    lon_0 = lons.mean()
    lat_0 = lats.mean()

    m = Basemap(lat_0=lat_0, lon_0=lon_0)
    lon, lat = np.meshgrid(lons, lats)
    xi, yi = m(lon, lat)

    plotData = np.squeeze(dataset.variables[variableName][timeIndex])
    cmap = plt.cm.prism
    cmap.set_bad('white',1.)
    cs = m.pcolormesh(xi, yi, plotData, shading='flat', cmap=cmap)
    # plt.imshow(plotData, cmap=plt.cm.jet)

    # 绘制经纬线
    m.drawparallels(np.arange(-90., 91., 20.), labels=[1,0,0,0], fontsize=10)
    m.drawmeridians(np.arange(-180., 181., 40.), labels=[0,0,0,1], fontsize=10)

    # m.drawcoastlines()
    # m.drawstates()
    # m.drawcountries()

    # Add Colorbar
    cbar = m.colorbar(cs, location='bottom', pad="10%")
    # plt.colorbar()
    # cbar.set_label(tlml_units)

    plt.title(variableName)
    plt.show()

    dataset.close()

plotNC('data/IBIS-out.nc', 'aylaiu', 0)
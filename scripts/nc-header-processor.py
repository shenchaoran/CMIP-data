from scipy import misc
import numpy as np
from netCDF4 import Dataset, default_fillvals

startYear = 2000
endYear = 2015
startDay = 1
endDay = 361
interval = 8

GRID_LENGTH = 0.5
LON_START = -179.75
LON_END = 179.75 + GRID_LENGTH
LAT_START = -54.75
LAT_END = 82.25 + GRID_LENGTH
scale = 0.1/interval

lons = np.arange(LON_START, LON_END, GRID_LENGTH)
lats = np.arange(LAT_START, LAT_END, GRID_LENGTH)

def mod17a2Header():
    mod17a2NC = '/home/scr/Data/MODIS/MOD17/A2/MOD17A2-GPP.nc'
    dataset = Dataset(mod17a2NC, 'r+', format='NETCDF4')

    lonDimension = dataset.dimensions['long']
    latDimension = dataset.dimensions['lat']
    timeDimension = dataset.dimensions['time']
    lonVariable = dataset.variables["long"]
    latVariable = dataset.variables["lat"]
    timeVariable = dataset.variables["time"]
    gppVariable = dataset.variables['GPP']
    
    # gppVariable.set_auto_mask(True)
    # gppVariable.setncattr('_FillValue', default_fillvals['f4'])
    # gppVariable.delncattr('missing_value')
    gppVariable[:] = np.ma.masked_where((gppVariable[:]<0)|(gppVariable[:]>409), gppVariable)

    dataset.close()

mod17a2Header()
from scipy import misc
import numpy as np
from netCDF4 import Dataset


srcFolder = '/home/scr/Data/MODIS/MOD17/A3/GeoTIFF_0.5degree/'
ncPath = srcFolder + '../MOD17A3-GPP-NPP.nc'
startYear = 2000
endYear = 2015
scale = 0.1/365

GRID_LENGTH = 0.5
LON_START = -179.75
LON_END = 179.75 + GRID_LENGTH
LAT_START = -54.75
LAT_END = 82.25 + GRID_LENGTH

LONS = np.arange(LON_START, LON_END, GRID_LENGTH)
LATS = np.arange(LAT_START, LAT_END, GRID_LENGTH)

dataset = Dataset(ncPath, 'w', format='NETCDF4')

lonDimension = dataset.createDimension('long', len(LONS))
latDimension = dataset.createDimension('lat', len(LATS))
timeDimension = dataset.createDimension('time', None)

lonVariable = dataset.createVariable("long", 'f4', ("long"))
latVariable = dataset.createVariable("lat", 'f4', ("lat"))
timeVariable = dataset.createVariable("time", 'f4', ("time"))

gppVariable = dataset.createVariable('GPP', 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=2)
nppVariable = dataset.createVariable('NPP', 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=2)
gppVariable.set_auto_mask(True)
nppVariable.set_auto_mask(True)
# gppVariable.setncattr('missing_value', -99999)
# nppVariable.setncattr('missing_value', -99999)

lonVariable.units = 'degrees_east'
latVariable.units = 'degrees_north'
timeVariable.units = 'days since ' + str(startYear) + '-01-01'
timeVariable.calendar = '365_day'

timeList = []
gppList = []
nppList = []

for i in range(endYear - startYear + 1):
    dth = i*365
    gppPath = '%sMOD17A3_Science_GPP_%s.tif' % (srcFolder, startYear+i)
    nppPath = '%sMOD17A3_Science_NPP_%s.tif' % (srcFolder, startYear+i)
    timeList.append(dth-1)
    band = misc.imread(gppPath)
    band = misc.imread(nppPath)
    gppCroped = band[2:277, :] * scale
    nppCroped = band[2:277, :] * scale
    gppList.append(gppCroped[::-1,:])
    nppList.append(nppCroped[::-1,:])
    progress = i*100/(endYear - startYear + 1)
    print('%.2f%%' % progress)

timeNA = np.array(timeList)
gppNA = np.array(gppList)
nppNA = np.array(nppList)
timeVariable[:] = timeNA
gppVariable[:] = gppNA
nppVariable[:] = nppNA
gppVariable[:] = np.ma.masked_where((gppVariable[:]<0)|(gppVariable[:]>17), gppVariable)
nppVariable[:] = np.ma.masked_where((nppVariable[:]<0)|(nppVariable[:]>17), nppVariable)

dataset.close()
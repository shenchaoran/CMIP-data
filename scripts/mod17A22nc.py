from scipy import misc
import numpy as np
from netCDF4 import Dataset


srcFolder = '/home/scr/Data/MODIS/MOD17/A2/GeoTIFF_0.5degree/'
ncPath = srcFolder + '../MOD17A2-GPP.nc'
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

LONS = np.arange(LON_START, LON_END, GRID_LENGTH)
LATS = np.arange(LAT_START, LAT_END, GRID_LENGTH)

def readNC():
    dataset = Dataset(ncPath, 'r+', format='NETCDF4')

    lonDimension = dataset.dimensions['long']
    latDimension = dataset.dimensions['lat']
    timeDimension = dataset.dimensions['time']
    lonVariable = dataset.variables['long']
    latVariable = dataset.variables['lat']
    timeVariable = dataset.variables['time']
    gppVariable = dataset.variables['GPP']

    print(gppVariable.shape)
    # timeVariable.datatype = 'f4'
    # timeVariable.units = 'days since ' + str(TIME_START) + '-01-01'
    # timeVariable.calendar = '365_day'

    # lonVariable[:] = LONS
    # latVariable[:] = LATS
    # timeVariable[:] = [n * 365 for n in range(YEAR_NUM)]
    # gppVariable.units = ''

    dataset.close()
    print('finished!')

def writeNC():
    dataset = Dataset(ncPath, 'w', format='NETCDF4')

    lonDimension = dataset.createDimension('long', len(LONS))
    latDimension = dataset.createDimension('lat', len(LATS))
    timeDimension = dataset.createDimension('time', None)

    lonVariable = dataset.createVariable("long", 'f4', ("long"))
    latVariable = dataset.createVariable("lat", 'f4', ("lat"))
    timeVariable = dataset.createVariable("time", 'f4', ("time"))

    gppVariable = dataset.createVariable('GPP', 'f4', ('time', 'lat', 'long'), zlib=True, least_significant_digit=2)
    # gppVariable.set_auto_mask(True)
    # gppVariable.setncattr('missing_value', 32767 * scale)

    lonVariable.units = 'degrees_east'
    latVariable.units = 'degrees_north'
    timeVariable.units = 'days since ' + str(startYear) + '-01-01'
    timeVariable.calendar = '365_day'

    timeList = []
    gppList = []

    numPerYear = (endDay+interval-startDay)/interval
    totalCount = (endYear-startYear+1)*numPerYear
    count = 0
    for i in range(endYear - startYear + 1):
        for j in np.arange(startDay, endDay + interval, interval):
            dth = i*365 + j
            tiffPath = '%sMOD17A2_GPP.A%s%s.tif' % (srcFolder, startYear+i, str(j).zfill(3))
            timeList.append(dth-1)
            band = misc.imread(tiffPath)
            croped = band[15:290, :] * scale
            gppList.append(croped[::-1,:])
            # im.close()
            progress = (i*numPerYear+ (j-startDay)/interval)*100/totalCount
            print('%.2f%%' % progress)

    timeVariable[:] = np.array(timeList)
    gppVariable[:] = np.array(gppList).astype(np.float32)
    gppVariable[:] = np.ma.masked_where((gppVariable[:]<0)|(gppVariable[:]>409), gppVariable)

    dataset.close()

# readNC()
writeNC()
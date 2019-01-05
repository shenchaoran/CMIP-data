const path = require('path')
const Bluebird = require('bluebird')
const fs = Bluebird.promisifyAll(require('fs'))

const obsFolder = 'E:/Data/CMIP/FLUXNET/LaThuile'
fs.
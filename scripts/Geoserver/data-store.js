const setting = require('./setting')
const request = require('request')
const requestAsync = require('request-promise')
const Bluebird = require('bluebird')
const fs = require('fs')
const BIOME_BGC_DAILY = require('../CMIP/MS/Biome_BGC-daily-cols.json')
const BIOME_BGC_ANNUGL = require('../CMIP/MS/Biome_BGC-annual-cols.json')
const BIOME_BGC_MONTH = BIOME_BGC_DAILY
const IBIS_DAILY = require('../CMIP/MS/IBIS-daily-cols.json')
const IBIS_ANNUGL = require('../CMIP/MS/IBIS-annual-cols.json')
const IBIS_MONTH = IBIS_ANNUGL
const LPJ_DAILY = require('../CMIP/MS/LPJ-daily-cols.json')
const LPJ_ANNUAL = require('../CMIP/MS/LPJ-annual-cols.json')
const LPJ_MONTH = LPJ_DAILY
const MOD17A2_DAILY = require('../CMIP/MS/MOD17A2-cols.json')
const MOD17A2_ANNUAL = require('../CMIP/MS/MOD17A2-annual-cols.json')
const MOD17A2_MONTH = MOD17A2_DAILY

const coverageStoreNames = {
    'grid-site': 'file:///usr/local/geoserver-2.15.1/data_dir/data/Carbon_Cycle/grid-site/grid-site.shp',
    'obs-site': 'file:///usr/local/geoserver-2.15.1/data_dir/data/Carbon_Cycle/obs-site/obs-site.shp',
}

const addDataStore = async (name) => {
    const datastore = {
        "dataStore": {
          "name": name,
          "type": "Shapefile",
          "enabled": true,
          "workspace": {
              "name": "Carbon_Cycle"
          },
          "_default": false,
          "connectionParameters": {
              "charset": "UTF-8",
              "filetype": "shapefile",
              "create spatial index": true,
              "memory mapped buffer": false,
              "enable spatial index": true,
              "url": `file:///usr/local/geoserver-2.15.1/data_dir/data/Carbon_Cycle/${name}/${name}.shp`,
              "fstype": "shape"
          }
        }
      }
    return requestAsync({
        url: `${setting.domain}/geoserver/rest/workspaces/Carbon_Cycle/datastores`,
        method: 'POST',
        headers: {
            'content-type': 'application/json',
            Authorization: 'Basic YWRtaW46Z2Vvc2VydmVy'
        },
        json: true,
        body: datastore
    }).then(() => requestAsync({
        url: `${setting.domain}/geoserver/rest/workspaces/Carbon_Cycle/datastores/${name}/external.shp?configure=all`,
        method: 'PUT',
        headers: {
            'content-type': 'text/plain',
            Authorization: 'Basic YWRtaW46Z2Vvc2VydmVy'
        },
        body: `file:///usr/local/geoserver-2.15.1/data_dir/data/Carbon_Cycle/${name}/${name}.shp`
    }))
}

const addDataStores = async () => {
    return Bluebird.map(['grid-site', 'obs-site'], dataStoreName => {
        return new Bluebird((resolve, reject) => {
            addDataStore(dataStoreName).then(res => resolve()).catch(e => resolve())
        })
    })
}

module.exports = addDataStores

// const main = async () => {
//     // await addSld('IBIS-avg', 'adaet', 0, 5.6, )
//     await addCoverageStores()
// }

// main()
//     .then(() => {
//         console.log('finished!')
//         process.exit(0)
//     })
//     .catch(e => {
//         console.error(e)
//         process.exit(1)
//     })
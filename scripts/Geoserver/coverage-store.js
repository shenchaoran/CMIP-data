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
    'IBIS': {
        cols: IBIS_ANNUGL,
        file: 'IBIS.nc'
    },
    'Biome-BGC': {
        cols: BIOME_BGC_ANNUGL,
        file: 'Biome-BGC.nc'
    },
    'LPJ': {
        cols: LPJ_ANNUAL,
        file: 'LPJ.nc'
    },
    'MOD17A2': {
        cols: MOD17A2_ANNUAL,
        file: 'MOD17A2.nc'
    },
}

const addCoverageStore = async (coveragestore) => {
    const url = `${setting.domain}/geoserver/rest/workspaces/Carbon_Cycle/coveragestores`
    return requestAsync({
        url,
        method: 'POST',
        headers: {
            'content-type': 'application/json',
            Authorization: 'Basic YWRtaW46Z2Vvc2VydmVy'
        },
        json: true,
        body: coveragestore
    })
}

const addCoverage = async (coveragestoreName, coverage) => {
    const url = `${setting.domain}/geoserver/rest/workspaces/Carbon_Cycle/coveragestores/${coveragestoreName}/coverages`
    return requestAsync({
        url,
        method: 'POST',
        headers: {
            'content-type': 'application/json',
            Authorization: 'Basic YWRtaW46Z2Vvc2VydmVy'
        },
        json: true,
        body: coverage
    })
    // .then(() => console.log(1))
    // .catch(e => {
    //     console.log(e)
    // })
}

const addCoverageStores = async () => {
    const request_coverageStore = [],
        request_coverage = []
    for(let coverageStoreName of Object.keys(coverageStoreNames)) {
        const fname = coverageStoreNames[coverageStoreName].file
        request_coverageStore.push({
            coverageStore: {
                name: coverageStoreName,
                type: 'NetCDF',
                enabled: true,
                workspace: {
                    name: 'Carbon_Cycle'
                },
                _default: false,
                url: `file:///home/scr/Data/scripts/data/annual/${fname}`,
            }
        })
        for(let col of coverageStoreNames[coverageStoreName].cols) {
            if(col.min != null && col.max != null) {
                request_coverage.push([
                    coverageStoreName,
                    {
                        coverage: {
                            name: `${coverageStoreName}-${col.id}`,
                            nativeName: col.id,
                            namespace: {
                                name: 'Carbon_Cycle'
                            },
                            title: `${coverageStoreName}-${col.id}`,
                            description: 'Generated from NetCDF',
                            enabled: true,
                            nativeFormat: 'NetCDF',
                            nativeCoverageName: col.id,
                            metadata: {
                                entry: [
                                    {
                                        '@key': 'time',
                                        dimensionInfo: {
                                            enabled: true,
                                            presentation: 'LIST',
                                            units: 'ISO8601',
                                            defaultValue: {
                                                strategy: 'MINIMUM'
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ])
            }
        }
    }
    return Bluebird.map(request_coverageStore, coverageStore => {
        return new Bluebird((resolve, reject) => {
            addCoverageStore(coverageStore).then(res => resolve()).catch(e => resolve())
        })
    }, {concurrency: 10})
    .then(res => {
        return Bluebird.map(request_coverage, v => {
            return new Bluebird((resolve, reject) => {
                addCoverage(...v).then(res => resolve()).catch(e => resolve())
            })
        }, {concurrency: 10})
    })
}

module.exports = addCoverageStores

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
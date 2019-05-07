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
    'IBIS': IBIS_ANNUGL,
    'Biome-BGC': BIOME_BGC_ANNUGL,
    'LPJ': LPJ_ANNUAL,
    'MOD17A2': MOD17A2_ANNUAL,
}

const updateLayerStyle = async (layerName, layer) => {
    const url = `${setting.domain}/geoserver/rest/workspaces/Carbon_Cycle/layers/${layerName}`
    return requestAsync({
        url,
        method: 'PUT',
        headers: {
            'content-type': 'application/json',
            Authorization: 'Basic YWRtaW46Z2Vvc2VydmVy'
        },
        json: true,
        body: layer
    })
}

const updateLayers = async () => {
    const tasks = []
    for(let coverageStoreName of Object.keys(coverageStoreNames)) {
        for(let col of coverageStoreNames[coverageStoreName]) {
            if(col.min != null && col.max != null) {
                tasks.push([
                    `${coverageStoreName}-${col.id}`,
                    {
                        layer: {
                            defaultStyle: {
                                name: `${coverageStoreName}-${col.id}`
                            },
                            opaque: true
                        }
                    }
                ])
            }
        }
    }
    return Bluebird.map(tasks, task => {
        return new Bluebird((resolve, reject) => {
            updateLayerStyle(...task).then(res => resolve()).catch(e => resolve())
        })
    })
}

const updatePointLayers = async () => {
    const seq = [
        {
            layerName: 'obs-site',
            body: {
                layer: {
                    defaultStyle: {
                        name: "obs-site"
                    }
                }
            }
        },
        {
            layerName: 'grid-site',
            body: {
                layer: {
                    defaultStyle: {
                        name: "grid-site"
                    }
                }
            }
        }
    ]
    return Bluebird.map(seq, item => {
        return requestAsync({
            url: `${setting.domain}/geoserver/rest/workspaces/Carbon_Cycle/layers/${item.layerName}`,
            method: 'PUT',
            headers: {
                'content-type': 'application/json',
                Authorization: 'Basic YWRtaW46Z2Vvc2VydmVy'
            },
            json: true,
            body: item.body,
        })
    })
}

module.exports = async () => {
    await updateLayers()
    await updatePointLayers()
}

// const main = async () => {
//     // await addSld('IBIS-avg', 'adaet', 0, 5.6, )
//     await updateLayers()
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
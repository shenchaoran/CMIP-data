const Bluebird = require('bluebird');
const path = require('path');
const fs = Bluebird.promisifyAll(require('fs'));
const child_process = require('child_process')
const setting = require('../setting')
const _ = require('lodash')
const exec = child_process.exec
const spawn = child_process.spawn
const stdId = '5b9012e4c29ca433443dcfab'
const siteIBIS = '/home/scr/Data/IBIS_Data/5b9012e4c29ca433443dcfab/IBIS_site_info.txt'
const folderLPJ = '/home/scr/Data/LPJ/5b9012e4c29ca433443dcfab/'
const lpjSuffix = '_grid.ascii'
const SITENUM = 61353
const indexMap = require('./data/index-map-sorted.json')

let getIBISsites = async () => {
    let siteStr = await fs.readFileAsync(siteIBIS, 'utf8')
    let sites = siteStr.split(/\n/g)
    // [index, long, lat]
    sites = sites.map((site, i) => {
        return [i+1].concat(site.split(/\s+/).map(v => parseFloat(v)))
    })
    // console.log(JSON.stringify(sites))
    return sites
}

let getFileMap = async () => {
    let sites = await getIBISsites()
    let maps = []
    let missedCount = 0
    await Bluebird.map(Array(SITENUM).fill(1).map((v, i) => v+i), i => {
        return fs.readFileAsync(path.join(folderLPJ, 'grid', i+lpjSuffix), 'utf8')
            .then(str => {
                // console.log(str.split(/\t/))
                let lonlat = str.split(/\t/).map(v => parseFloat(v))
                let site = _.find(sites, site => site[1] == lonlat[0] && site[2] == lonlat[1])
                if(site) {
                    // [LPJ-index, stdIndex]
                    maps.push([i, site[0]])
                }
                else {
                    missedCount++
                    // console.log(lonlat, '  not found')
                    // console.log(i)
                }
            })
    }, {
        concurrency: 10
    })
    // console.log(maps.length, missedCount)
    await fs.writeFileAsync('./data/index-map.json', JSON.stringify(maps), 'utf8')
    return maps
}

let sortIndexMap = async () => {
    let sorted = indexMap.sort((v1, v2) => {
        return v1[1] - v2[1]
    })
    await fs.writeFileAsync('./data/index-map-sorted.json', JSON.stringify(sorted), 'utf8')
}

let renameFiles = async () => {
    // let fsMap = await getFileMap()
    let fsMap = indexMap
    Bluebird.map(fsMap, ([lpjIndex, stdIndex]) => {
        let pathMap = [
            {
                folder: 'met/cld',
                suffix: '_cld.ascii',
                distSuffix: '.cld.csv'
            },
            {
                folder: 'met/prec',
                suffix: '_prec.ascii',
                distSuffix: '.prec.csv'
            },
            {
                folder: 'met/temp',
                suffix: '_temp.ascii',
                distSuffix: '.temp.csv'
            },
            {
                folder: 'grid',
                suffix: '_grid.ascii',
                distSuffix: '.grid.csv'
            },
            {
                folder: 'outputs',
                suffix: '.daily.ascii',
                distSuffix: '.daily.csv'
            },
        ]
        return Bluebird.map(pathMap, item => {
            let srcPath = `${folderLPJ}${item.folder}/${lpjIndex}${item.suffix}`,
                distPath = `${folderLPJ}${item.folder}/${stdIndex}${item.distSuffix}`;
            return new Bluebird((resolve, reject) => {
                try{
                    fs.rename(srcPath, distPath, (err, ) => {
                        return resolve()
                    })
                }
                catch(e) {
                    if(e.code != 'ENOENT')
                        console.log('error: ', stdIndex)
                    return resolve()
                }
            })
        })
        .then(() => console.log(stdIndex))
    }, {
        concurrency: 3
    })
}

let main = async () => {
    // await getIBISsites()
    // await getFileMap()
    // await sortIndexMap()
    renameFiles()
}

main()
const path = require('path')
const Bluebird = require('bluebird')
const fs = Bluebird.promisifyAll(require('fs'))
const _ = require('lodash')
let fluxnetSites = require('./FLUXNET2015-sites-db.js')
const child_process = require('child_process')

const obsFolder = 'E:/Data/CMIP/FLUXNET/LaThuile'
const distFolder = 'E:/Data/CMIP/FLUXNET/refactored'
const gridFile = 'E:/Data/IBIS_Data/5b9012e4c29ca433443dcfab/input/IBIS_site_info.txt'
const GRID_LENGTH = 0.5
const LON_START = -179.75
const LON_END = 179.75 + GRID_LENGTH
const LAT_START = -54.75
const LAT_END = 82.25 + GRID_LENGTH

let fn = async () => {
    let fslist = await fs.readdirAsync(obsFolder)
    let sites = []
    fslist.map(fs => {
        let group = fs.match(/^(\w+-\w+)\.(\d+)\.synth\.daily\.allvars\.csv$/)
        if (group && group.length === 3) {
            // let site = _.find(sites, site => site.SITE_ID === group[1])
            // if(!site) {
            //     console.log(`${group[1]} not found!`)
            //     return
            // }
            // let year = parseInt(group[2])
            // if(!site.LaThuileStart || site.LaThuileStart> year)
            //     site.LaThuileStart = year
            // if(!site.LaThuileEnd || site.LaThuileEnd< year)
            //     site.LaThuileEnd = year

            let site = _.find(sites, site => site.id === group[1])
            let year = parseInt(group[2])
            if (!site) {
                // TODO lat & long
                site = {
                    id: group[1],
                }
                sites.push(site)
                let fluxnetSite = _.find(fluxnetSites, site => site.SITE_ID === group[1])
                if (fluxnetSite) {
                    site.lat = parseFloat(_.get(fluxnetSite, 'GRP_LOCATION.LOCATION_LAT'))
                    site.long = parseFloat(_.get(fluxnetSite, 'GRP_LOCATION.LOCATION_LONG'))
                    site.name = _.get(fluxnetSite, 'SITE_NAME')
                    site.url = _.get(fluxnetSite, 'URL_AMERIFLUX')
                }
            }
            if (!site.startTime || site.startTime > year)
                site.startTime = year
            if (!site.endTime || site.endTime < year)
                site.endTime = year
        } else {
            return null;
        }
    }).filter(e => !!e)


    return sites;
}

let parseGrid = async () => {
    let str = await fs.readFileAsync(gridFile, 'utf8')
    str = str.trim();
    const rows = str.split(/\r\n|\r|\n/g);
    const docs = _
        .chain(rows)
        .filter(item => item !== '')
        .map((row, i) => {
            const temp = row.split(/\s/);
            if(temp.length >= 2) {
                return {
                    index: i+1,
                    long: parseFloat(temp[0]),
                    lat: parseFloat(temp[1])
                };
            }
        })
        .filter(item => item != undefined)
        .value();
    return docs
}

let sites = fn()
    .then(async sites => {
        sites = sites.filter(site => site.lat && site.long)
        let grid = await parseGrid()
        sites.map(site => {
            let llong, rlong, llat, rlat, sortedLat, sortedLong;
            llong = Math.floor((site.long - LON_START)/GRID_LENGTH) * GRID_LENGTH + LON_START
            rlong = llong + GRID_LENGTH
            llat = Math.floor((site.lat - LAT_START)/GRID_LENGTH) * GRID_LENGTH + LAT_START
            rlat = llat + GRID_LENGTH
            if(Math.abs(llong - site.long) > GRID_LENGTH/2) {
                sortedLong = [rlong, llong]
            }
            else 
                sortedLong = [llong, rlong]
            if(Math.abs(llat - site.lat) > GRID_LENGTH/2) {
                sortedLat = [rlat, llat]
            }
            else 
                sortedLat = [llat, rlat]
            
            let pts = [
                [sortedLong[0], sortedLat[0]],
                [sortedLong[0], sortedLat[1]],
                [sortedLong[1], sortedLat[0]],
                [sortedLong[1], sortedLat[1]],
            ]
            let gpt
            for(let pt of pts) {
                gpt = _.find(grid, gpt => gpt.lat === pt[1] && gpt.long === pt[0])
                if(gpt)
                    break;
            }
            if(gpt)
                site.index = gpt.index
        })

        sites = sites.filter(site => !!site.index)
        let validSites = []
        await Bluebird.map(sites, async site => {
            try {
                await fs.accessAsync(path.join(distFolder, `${site.id}.csv`), fs.constants.F_OK)
                validSites.push(site)
            }
            catch(e) {
                e    
            }
        })

        let features = validSites.map(site => {
            return {
                type: 'Feature',
                geometry: {
                    type: 'Point',
                    coordinates: [site.long, site.lat]
                },
                properties: site
            }
        })
        let geojson = {
            type: 'FeatureCollection',
            features
        }
        fs.writeFile(path.join(obsFolder, '../obs-site.json'), JSON.stringify(geojson), 'utf8', err => {
            if(!err) {
                child_process.exec('C:/OSGeo4W64/bin/ogr2ogr -F "ESRI Shapefile" obs-site.shp obs-site.json OGRGeoJSON', {
                    cwd: path.join(obsFolder, '..')
                }, (err, stdout, stderr) => {
                    if(err) {
                        err;
                    }
                    console.log(stdout)
                    console.error(stderr);
                })
            }
        })
    })
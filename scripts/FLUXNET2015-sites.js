const path = require('path')
const Bluebird = require('bluebird')
const fs = Bluebird.promisifyAll(require('fs'))
const _ = require('lodash')
let fluxnetSites = require('./FLUXNET2015-sites-db.js')
const child_process = require('child_process')

const obsFolder = 'E:/Data/Fluxdata'
const gridFile = 'E:/Data/IBIS_Data/5b9012e4c29ca433443dcfab/input/IBIS_site_info.txt'
const GRID_LENGTH = 0.5
const LON_START = -179.75
const LON_END = 179.75 + GRID_LENGTH
const LAT_START = -54.75
const LAT_END = 82.25 + GRID_LENGTH

let getGridPts = async () => {
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

let getObsSites = async () => {
    let gridPts = await getGridPts()
    // fluxnetSites = fluxnetSites.filter(site => site.lat && site.long)
    let sites = fluxnetSites.map(fluxnetSite => {
        let llong, rlong, llat, rlat, sortedLat, sortedLong, site = {
            id: fluxnetSite.SITE_ID,
            name: fluxnetSite.SITE_NAME,
            url: fluxnetSite.URL_AMERIFLUX,
            lat: parseFloat(fluxnetSite.GRP_LOCATION.LOCATION_LAT),
            long: parseFloat(fluxnetSite.GRP_LOCATION.LOCATION_LONG),
            elevation: parseFloat(fluxnetSite.GRP_LOCATION.LOCATION_ELEV),
            PFT: fluxnetSite.IGBP,
            GRP_CLIM_AVG: fluxnetSite.GRP_CLIM_AVG,
            tier1: fluxnetSite.Tier1,
            tier2: fluxnetSite.Tier2,
            startTime: parseInt(fluxnetSite.Tier2.split('-')[0]),
            endTime: parseInt(fluxnetSite.Tier2.split('-')[1]),
        };
        
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
            gpt = _.find(gridPts, gpt => gpt.lat === pt[1] && gpt.long === pt[0])
            if(gpt)
                break;
        }
        if(gpt)
            site.index = gpt.index
        return site
    })
    return sites
}

let writeSite2Shp = async () => {
    let sites = await getObsSites();
    sites = sites.filter(site => !!site.index)

    let geojson = {
        type: 'FeatureCollection',
        features: sites.map(site => {
            return {
                type: 'Feature',
                geometry: {
                    type: 'Point',
                    coordinates: [site.long, site.lat]
                },
                properties: site
            }
        })
    }
    fs.writeFile(path.join(obsFolder, 'tier-2-sites.json'), JSON.stringify(geojson), 'utf8', err => {
        if(!err) {
            child_process.exec('ogr2ogr -f "ESRI Shapefile" tier-2-sites.shp tier-2-sites.json OGRGeoJSON', {
                cwd: obsFolder
            }, (err, stdout, stderr) => {
                if(err) {
                    err;
                }
                console.log(stdout)
                console.error(stderr);
            })
        }
    })
}

let copyFluxnetData = async () => {
    let srcFolder = 'E:/Data/Fluxdata/Tier 2 subset',
        distFolder = 'E:/Data/Fluxdata/Tier 2 renamed',
        count = 0;
    
    let fslist = await fs.readdirAsync(srcFolder, {withFileTypes: true})
    await Bluebird.map(fslist, file => {
        return new Bluebird(async (resolve, reject) => {
            if(file.isDirectory()) {
                let group = file.name.match(/^\w+_(.*)_FLUXNET2015_SUBSET_(\d+-\d+_\d-\d)$/)
                if(group.length !== 3){
                    console.log(file.name)
                    return resolve()
                }
                else {
                    let siteName = group[1];
                    let fname = `FLX_${siteName}_FLUXNET2015_SUBSET_DD_${group[2]}.csv`;
                    let fpath = path.join(srcFolder, file.name, fname);
                    let distpath = path.join(distFolder, `${siteName}.csv`)
                    try {
                        await fs.accessAsync(fpath, fs.constants.F_OK)
                        await fs.copyFileAsync(fpath, distpath)
                        count++;
                        return resolve()
                    }
                    catch(e) {
                        e
                        return resolve(); 
                    }
                }
            }
            else {
                return resolve()
            }
        })
    })
    console.log('copied number: ', count)
}

let getPFTs = async () => {
    let sites = await getObsSites();
    sites = sites.filter(site => !!site.index)
    let pfts = new Set()
    sites.map(site => {
        pfts.add(site.PFT)
    })
    console.log(Array.from(pfts).length);
    return pfts
}

var main = async () => {
    // let fluxnetSites = await getObsSites();
    
    // await writeSite2Shp();
    
    // await copyFluxnetData();

    let pfts = await getPFTs()
}

main()
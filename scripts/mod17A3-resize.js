const Bluebird = require('bluebird');
const path = require('path');
const fs = Bluebird.promisifyAll(require('fs'));
const child_process = require('child_process')
const setting = require('../setting')
const exec = child_process.exec
const spawn = child_process.spawn
const _ = require('lodash')
const srcFolder = '/home/scr/Data/MODIS/MOD17/A3/GeoTIFF_30arcsec',
    distFolder = `${srcFolder}/../GeoTIFF_0.5degree`,
    startYear = 2000,
    endYear = 2015;

let failedList = new Set()
let count = 0;
const resizeTiff = async (task) => {
    try {
        try {
            await fs.accessAsync(task[1], fs.constants.F_OK)
        }
        catch(e) {
            if(e.code === 'ENOENT') {
                const cp = spawn('gdalwarp', [
                    '-te',
                    -180, -60, 180, 80,
                    '-ts',
                    720,
                    280,
                    task[0],
                    task[1],
                ])
                return new Bluebird((resolve, reject) => {
                    cp.stdout.on('data', data => {
                        // console.log(data.toString())
                    })
                    cp.stderr.on('data', err => {
                        // console.log(err.toString())
                    })
                    cp.on('close', code => {
                        count++;
                        console.log(count);
                        if(code === 0) {
                            return resolve()
                        }
                        else {
                            failedList.add(task[0])
                            return resolve()
                        }
                    })
                })
            }
        }
    }
    catch(e) {
        console.error(`------ ${task[0]} failed`)
    }
}

try {
    let tasks = [];
    for(let i=startYear; i<endYear+1; i++) {
        let sPath = `${srcFolder}/MOD17A3_Science_NPP_${i}.tif`,
            dPath = `${distFolder}/MOD17A3_Science_NPP_${i}.tif`;
        tasks.push([sPath, dPath])
    }

    Bluebird.map(tasks, resizeTiff, { concurrency: 4 }).then(async v => {
        let logPath = path.join(distFolder, 'batch.log')
        await fs.writeFileAsync(logPath, JSON.stringify(failedList), 'utf8')
        console.log('finished!')
    })
    .catch(e => {
        console.error(e)
    })
}
catch(e) {
    console.error(e)
}


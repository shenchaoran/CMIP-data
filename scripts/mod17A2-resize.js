const Bluebird = require('bluebird');
const path = require('path');
const fs = Bluebird.promisifyAll(require('fs'));
const child_process = require('child_process')
const setting = require('../setting')
const exec = child_process.exec
const spawn = child_process.spawn
const _ = require('lodash')
const srcFolder = '/home/scr/Data/MODIS/MOD17/A2/GeoTIFF_0.05degree',
    distFolder = `${srcFolder}/../GeoTIFF_0.5degree`,
    startYear = 2000,
    endYear = 2015,
    startDay = 1,
    endDay = 361,
    interval = 8;

let failedList = new Set()
let count = 0;
let SUM = 690;
const resizeTiff = async (task) => {
    try {
        try {
            await fs.accessAsync(task[1], fs.constants.F_OK)
        }
        catch(e) {
            if(e.code === 'ENOENT') {
                const cp = spawn('gdalwarp', [
                    '-te',
                    -180, -90, 180, 90,
                    '-ts',
                    720,
                    360,
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
                        if(count%20 === 0)
                            console.info(count*100/SUM + '%');
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
        for(let j=startDay; j<endDay+interval; j+=interval) {
            let dth = _.padStart(j, 3, '0'),
                sPath = `${srcFolder}/MOD17A2_GPP.A${i}${dth}.tif`,
                dPath = `${distFolder}/MOD17A2_GPP.A${i}${dth}.tif`;
            tasks.push([sPath, dPath])
        }
    }

    Bluebird.map(tasks, resizeTiff, { concurrency: 30 }).then(async v => {
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


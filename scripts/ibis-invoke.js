const Bluebird = require('bluebird');
const path = require('path');
const fs = Bluebird.promisifyAll(require('fs'));
const child_process = require('child_process')
const setting = require('../setting')
const exec = child_process.exec
const spawn = child_process.spawn
const stdId = '5b9012e4c29ca433443dcfab'
const stdPath = path.join(__dirname, `../IBIS_Data/${stdId}`)

let count = 0
const SUM = 40595
let failedList = new Set()
const invokeModel = async (i) => {
    try {
        try {
            await fs.accessAsync(path.join(stdPath, 'outputs', `${i}.daily.txt`), fs.constants.F_OK)
        }
        catch(e){
            if(e.code === 'ENOENT') {
                let paras = [
                    `--met=${stdPath}/input/csv/${i}_proced.csv`,
                    `--site=${stdPath}/input/txt/${i}.txt`,
                    `--do=${stdPath}/outputs/${i}.daily.txt`,
                    `--ao=${stdPath}/outputs/${i}.annual.txt`,
                    `--stat=${stdPath}/outputs/${i}.state.txt`,
                    // '--spinup=1'
                ]
                const cp = spawn(path.join(__dirname, '../IBIS_Data/IBIS.exe'), paras)
                return new Bluebird((resolve, reject) => {
                    cp.stdout.on('data', data => {
                        // console.log(data.toString())
                    })
                    cp.stderr.on('data', err => {
                        console.error(data.toString())
                    })
                    cp.on('close', code => {
                        count++;
                        if(count%20 === 0)
                            console.info(count*100/SUM + '%');
                        if(code === 0) {
                            return resolve()
                        }
                        else {
                            failedList.add(i)
                            return resolve()
                        }
                    })
                })
            }
        }
    }
    catch(e) {
        console.error(`------ ${i} failed`)
    }
}

try {

    // invokeModel(1)

    let files = Array(SUM).fill(1).map((v, i) => v+i)
    Bluebird.map(files, invokeModel, { concurrency: 7 }).then(async v => {
        let logPath = path.join(stdPath, 'batch.log')
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
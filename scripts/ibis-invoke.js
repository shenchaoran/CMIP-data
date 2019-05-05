const Bluebird = require('bluebird');
const path = require('path');
const fs = Bluebird.promisifyAll(require('fs'));
const child_process = require('child_process')
const setting = require('../setting')
const exec = child_process.exec
const spawn = child_process.spawn
const stdId = '5b9012e4c29ca433443dcfab'
const stdPath = path.join(__dirname, `../IBIS_Data/${stdId}`)
const logPath = path.join(__dirname, './logs/IBIS-invoke-failed.log')

let count = 0
const SUM = 40595
let failedList = new Set()
let core = 8

if(process.argv.length > 2) {
    for(let i=2; i< process.argv.length; i++) {
        let argc = process.argv[i]
        if(argc.startsWith('--core')) {
            core = parseInt(argc.replace('--core=', '').trim())
        }
    }
}

const invokeModel = async (i) => {
    try {
        try {
            // let err = new Error('file size is 0')
            // err.code = 'ENOENT'
            // throw err

            let fpath = path.join(stdPath, 'outputs', `${i}.state.txt`)
            await fs.accessAsync(fpath, fs.constants.F_OK)
            let stat = await fs.statAsync(fpath)
            // console.log(stat.size)
            if(stat.size === 0 || stat.size === '0n' || stat.size === '0') {
                // console.log('file size is 0')
                let err = new Error('file size is 0')
                err.code = 'ENOENT'
                throw err
            }

            count++;
            if(count%20 === 0)
                console.info(count*100/SUM + '%');
        }
        catch(e){
            if(e.code === 'ENOENT') {
                let paras = [
                    `--met=${stdPath}/met/${i}_proced.csv`,
                    `--site=${stdPath}/site/${i}.txt`,
                    `--do=${stdPath}/outputs/${i}.daily.txt`,
                    `--ao=${stdPath}/outputs/${i}.annual.txt`,
                    `--stat=${stdPath}/outputs/${i}.state.txt`,
                    '--spinup=100'
                ]
                const cp = spawn(path.join(__dirname, '../IBIS_Data/IBIS'), paras)
                return new Bluebird((resolve, reject) => {
                    cp.stdout.on('data', data => {
                        // console.log(data.toString())
                    })
                    cp.stderr.on('data', err => {
                        // console.error(err.toString())
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

var invokeOne = async i => invokeModel(i)
var invokeBatch = async () => {
    let files = Array(SUM).fill(1).map((v, i) => v+i)
    return Bluebird.map(files, invokeModel, { concurrency: core }).then(async v => {
        await fs.writeFileAsync(logPath, JSON.stringify(Array.from(failedList)), 'utf8')
        console.log('finished!')
    })
    .catch(e => {
        console.error(e)
    })
}
var invokeError = async () => {
    try {
        let str = await fs.readFile(logPath, 'utf8')
        let files = str.match(/\d+/g)
        return Bluebird.map(files, invokeModel, { concurrency: core }).then(async v => {
            await fs.writeFileAsync(logPath, JSON.stringify(Array.from(failedList)), 'utf8')
            console.log('finished!')
        })
        .catch(e => {
            console.error(e)
        })
    }
    catch(e) {
        
    }
}

var main = async () => {
    // invokeOne(40)
    invokeBatch()
    // invokeError()
}

main()
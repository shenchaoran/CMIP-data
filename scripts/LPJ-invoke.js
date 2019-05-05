const Bluebird = require('bluebird');
const path = require('path');
const fs = Bluebird.promisifyAll(require('fs'));
const child_process = require('child_process')
const setting = require('../setting')
const exec = child_process.exec
const spawn = child_process.spawn
const stdId = '5b9012e4c29ca433443dcfab'
const stdPath = path.join(__dirname, `../LPJ/${stdId}`)

let count = 0
const SUM = 40595
const start = 40595
const end = 61353
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
            let fpath = path.join(stdPath, 'outputs', `${i}.daily.ascii`)
            await fs.accessAsync(fpath, fs.constants.F_OK)
            let stat = await fs.statAsync(fpath)
            if(stat.size === 0 || stat.size === '0n' || stat.size === '0') {
                let err = new Error('file size is 0')
                err.code = 'ENOENT'
                throw err
            }
        }
        catch(e){
            if(e.code === 'ENOENT') {
                let paras = [
                    `--config=${stdPath}/config.txt`,
                    `--outfile=${stdPath}/outputs/${i}.daily.ascii`,
                    `--grid=${stdPath}/grid/${i}_grid.ascii`,
                    `--soil=${stdPath}/soil/${i}_soil.ascii`,
                    `--co2=${stdPath}/co2-1982-2013.txt`,
                    `--temp=${stdPath}/met/temp/${i}_temp.ascii`,
                    `--prec=${stdPath}/met/prec/${i}_prec.ascii`,
                    `--cloud=${stdPath}/met/cld/${i}_cld.ascii`,
                    `--dayl=${stdPath}/dayl.ascii`,
                ]
                // console.log(paras)
                const cp = spawn(path.join(__dirname, '../LPJ/LPJ'), paras)
                // console.log('start')
                return new Bluebird((resolve, reject) => {
                    cp.stdout.on('data', data => {
                        // console.log(data.toString())
                    })
                    cp.stderr.on('data', err => {
                        // console.error(data.toString())
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

let main = async () => {
    try {
        // await invokeModel(1)
    
        let files = Array(end - start + 1).fill(start).map((v, i) => v+i)
        // let str = await fs.readFile(path.join(__dirname, 'data/LPJ-error.log'), 'utf8')
        // let files = str.match(/\d+/g)
        await Bluebird.map(files, invokeModel, { concurrency: core })
        let logPath = path.join(stdPath, 'batch.log')
        await fs.writeFileAsync(logPath, JSON.stringify(failedList), 'utf8')
        console.log('finished!')
    }
    catch(e) {
        console.error(e)
    }
    
}
main()

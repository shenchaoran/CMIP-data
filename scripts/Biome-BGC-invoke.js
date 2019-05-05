const Bluebird = require('bluebird');
const path = require('path');
const fs = Bluebird.promisifyAll(require('fs'));
const child_process = require('child_process')
const setting = require('../setting')
const exec = child_process.exec
const spawn = child_process.spawn
const stdId = '5b9012e4c29ca433443dcfab'
const stdPath = path.join(__dirname, `../Biome_BGC_Data/${stdId}`)

let count = 0
const SUM = 40595
let failedList = new Set()
const invokeModel = async (i) => {
    try {
        try {
            await fs.accessAsync(path.join(stdPath, 'outputs', `${i}.daily.ascii`), fs.constants.F_OK)
        }
        catch(e) {
            // if(e.code === 'ENOENT') {

            // }
            let epc = 'shrub';
            let ini = await fs.readFileAsync(`${stdPath}/ini/${i}.ini`, 'utf8')
            let reg = new RegExp(/epc\/(.*)\.epc/)
            rst = reg.exec(ini)
            if(rst) 
                epc = rst[1]
    
            let js = path.join(__dirname, '../Biome_BGC_Data/Biome_BGC.js')
            let paras = [
                js,
                '-a',
                `--i=${stdPath}/ini/${i}.ini`,
                `--m=${stdPath}/met/${i}.mtc43`,
                `--ri=${stdPath}/outputs/${i}.endpoint`,
                `--ro=${stdPath}/outputs/${i}.endpoint`,
                `--co2=${stdPath}/co2/co2.txt`,
                `--epc=${stdPath}/epc/${epc}.epc`,
                `--o=${stdPath}/outputs/${i}`,
            ]
            const cp = spawn('node', paras)
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
                        failedList.add(i)
                        return resolve()
                    }
                })
            })
        }
    }
    catch(e) {
        console.error(`------ ${i} failed`)
    }
}

try {

    // invokeModel(1)

    let files = Array(SUM).fill(1).map((v, i) => v+i)
    Bluebird.map(files, invokeModel, { concurrency: 20 }).then(async v => {
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
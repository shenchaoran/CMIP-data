const Bluebird = require('bluebird');
const path = require('path');
const fs = Bluebird.promisifyAll(require('fs'));
const child_process = require('child_process')
const setting = require('../setting')
const exec = child_process.exec
const spawn = child_process.spawn
const stdId = '5b9012e4c29ca433443dcfab'
const stdPath = path.join(__dirname, `../Biome_BGC_Data/${stdId}`)

let getFinished = async () => {
    let hadRunned = new Set()
    let fslist = await fs.readdirAsync(path.join(stdPath, 'outputs'))
    fslist.map(fname => {
        if(fname.isFile()) {

        }
    })
    return hadRunned;
}


let main = async () => {
    try {
        let files = Array(SUM).fill(1).map((v, i) => v+i)
        let runnedList = await getFinished()
        files = files.map(v => !runnedList.has(v))
        
    }
    catch(e) {
        console.error(e)
    }
}

main()

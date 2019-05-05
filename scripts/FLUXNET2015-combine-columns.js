// 将多列合并相加
const path = require('path')
const Bluebird = require('bluebird')
const fs = Bluebird.promisifyAll(require('fs'))
const _ = require('lodash')

var combineColumns = async () => {
    let srcFolder = 'E:/Data/Fluxdata/Tier 2 renamed',
        distFolder = 'E:/Data/Fluxdata/Tier 2 combined';
    let fslist = await fs.readdirAsync(srcFolder)
    await Bluebird.map(fslist, fname => {
        return new Bluebird((resolve, reject) => {
            let argv = {
                srcPath: path.join(srcFolder, fname),
                distPath: path.join(distFolder, fname),
                columns: {
                    GPP: [
                        'GPP_NT_VUT_REF',
                        'GPP_DT_VUT_REF'
                    ],
                    NPP: [

                    ],
                    NEP: [
                        'NEE_VUT_REF'
                    ],
                    RECO: [
                        'RECO_NT_VUT_REF',
                        'RECO_DT_VUT_REF',
                        'RECO_SR',
                    ]
                }
            }
        })
    }, {
        concurrency: 10
    })
}

var main = async () => {
    await combineColumns();
}

main()
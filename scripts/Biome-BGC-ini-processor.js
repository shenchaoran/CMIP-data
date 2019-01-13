const Bluebird = require('bluebird');
const path = require('path');
const fs = Bluebird.promisifyAll(require('fs'));
let count = 0;

const convertINI = async (i, type) => {
    try {
        var fileName = type === 'spinup'? `${i}_spinup.ini`: `${i}.ini`
        var testFP = path.join(__dirname, '../Biome_BGC_Data/5b9012e4c29ca433443dcfab/ini', fileName)
        var str = await fs.readFileAsync(testFP, 'utf8')
        str = str.replace(/(OUTPUT_CONTROL.*\n)([\s\S]*?)(.*\nDAILY_OUTPUT)/m, (match, p1, p2, p3, offset, str) => {
            if(type === 'spinup')
                return `${p1}outputs/${i}     (text) prefix for output files
0   (flag)  1 = write daily output   0 = no daily output
0   (flag)  1 = monthly avg of daily variables  0 = no monthly avg
0   (flag)  1 = annual avg of daily variables   0 = no annual avg
0   (flag)  1 = write annual output  0 = no annual output
1   (flag)  for on-screen progress indicator
${p3}`;
            else 
                return `${p1}outputs/${i}     (text) prefix for output files
1   (flag)  1 = write daily output   0 = no daily output
0   (flag)  1 = monthly avg of daily variables  0 = no monthly avg
1   (flag)  1 = annual avg of daily variables   0 = no annual avg
1   (flag)  1 = write annual output  0 = no annual output
1   (flag)  for on-screen progress indicator
${p3}`;
        });

        if(type !== 'spinup') {
            str = str.replace(/(DAILY_OUTPUT.*\n)([\s\S]*?)(.*\nEND_INIT)/m, (match, p1, p2, p3, offset, str) => {
                return `${p1}4    (int) number of daily variables to output
623    0 gpp;
620    1 npp;
621    2 nep;
622    3 nee;

ANNUAL_OUTPUT    (keyword)
4    (int)   number of annual output variables
623    0 gpp;
620    1 npp;
621    2 nep;
622    3 nee;
${p3}`
            })
        }
        
        await fs.writeFileAsync(testFP, str, 'utf8')
        count++;
        console.info(count);
    }
    catch(e) {
        console.error(`------ ${i} failed`)
    }
}

// const testFile = 1
// let fn = async () => {
//     await convertINI(testFile, 'normal')
//     await convertINI(testFile, 'spinup')
// }
// fn()

try {
    let files = Array(40595).fill(1).map((v, i) => v+i)
    Bluebird.map(files, file => {
        return convertINI(file, 'spinup')
    }, { concurrency: 1000 }).then(v => {
        console.log('finished!')
    })
    .catch(e => {
        console.log(e)
    })
}
catch(e) {
    console.error(e)
}
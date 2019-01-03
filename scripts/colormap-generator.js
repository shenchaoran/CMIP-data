// https://www.npmjs.com/package/colormap

const colormap = require('colormap')
const cmGemerator = (cmName, min, max, count, noDataV) => {
    let colors = colormap({
        colormap: cmName,
        nshades: count,
        format: 'hex',
        alpha: 1
    })
    let cmStr = '',
        delta = (max - min)/ count;
    for(let i=0; i< count; i++) {
        let quantity = delta * i + min
        cmStr += `<ColorMapEntry color="${colors[i]}" quantity="${quantity}" />\n`
    }
    if(noDataV)
        cmStr += `<ColorMapEntry color="#fff" quantity="${noDataV}" opacity="0" />\n`

    return cmStr
}

// let rst = cmGemerator('hsv', 0, 10, 100, 11)
let rst = cmGemerator('hsv', 0, 0.000624742, 100)

let ibis_falll = cmGemerator('hsv', 0, 0.682617, 100)
let ibis_fallw = cmGemerator('hsv', 0, 0.470703, 100)
let ibis_aylail = cmGemerator('hsv', 0, 5.84961, 100)
let ibis_aylaiu = cmGemerator('hsv', 0, 7.7998, 100)
let ibis_ayco2mic = cmGemerator('hsv', 0, 922.097, 100)

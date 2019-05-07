const setting = require('./setting')
const request = require('request')
const requestAsync = require('request-promise')
const Bluebird = require('bluebird')
const fs = require('fs')
const _ = require('lodash')
const BIOME_BGC_DAILY = require('../CMIP/MS/Biome_BGC-daily-cols.json')
const BIOME_BGC_ANNUGL = require('../CMIP/MS/Biome_BGC-annual-cols.json')
const BIOME_BGC_MONTH = BIOME_BGC_DAILY
const IBIS_DAILY = require('../CMIP/MS/IBIS-daily-cols.json')
const IBIS_ANNUGL = require('../CMIP/MS/IBIS-annual-cols.json')
const IBIS_MONTH = IBIS_ANNUGL
const LPJ_DAILY = require('../CMIP/MS/LPJ-daily-cols.json')
const LPJ_ANNUAL = require('../CMIP/MS/LPJ-annual-cols.json')
const LPJ_MONTH = LPJ_DAILY
const MOD17A2_DAILY = require('../CMIP/MS/MOD17A2-cols.json')
const MOD17A2_ANNUAL = require('../CMIP/MS/MOD17A2-annual-cols.json')
const MOD17A2_MONTH = MOD17A2_DAILY

const coverageStoreNames = {
    'IBIS-avg': IBIS_ANNUGL,
    'Biome-BGC-avg': BIOME_BGC_ANNUGL,
    'LPJ-avg': LPJ_ANNUAL,
    'MOD17A2-avg': MOD17A2_ANNUAL,
}

const CM_Gemerator = (sldName, cmName, min, max, noDataVs, colors) => {
    let cmStr = '';
    const count = colors.length;
    const delta = (max - min)/(count-1);
    // if(noDataVs)
    //     noDataVs.map(noDataV => {
    //         cmStr += `<ColorMapEntry color="#fff" quantity="${noDataV}" opacity="0" />\n`
    //     })
    let getNumberSigLen = (v) => {
        let g = ('' + v).match(/\.(.*)/)
        if(g && g.length)
            return g[1].length
        else 
            return 0
    }
    const fixedLength = Math.max(getNumberSigLen(min), getNumberSigLen(max)) + 1
    let stops = []
    for(let i=0; i< count; i++) {
        let quantity = (delta * i + min).toFixed(fixedLength)
        stops.push(parseFloat(quantity))
    }
    if (_.indexOf(stops, 0) === -1) {
        stops.push(0)
    }
    stops = stops.sort((v1,v2) => v1-v2)
    let i=0
    stops.map(stop => {
        if(stop === 0) {
            cmStr += `<ColorMapEntry color="#ffffff" quantity="${stop}" opacity="0" />\n`
        }
        else {
            cmStr += `<ColorMapEntry color="${colors[i]}" quantity="${stop}" />\n`
            i++
        }
    })
    return `<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0" 
    xmlns="http://www.opengis.net/sld" 
    xmlns:ogc="http://www.opengis.net/ogc"
    xmlns:xlink="http://www.w3.org/1999/xlink" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd">
    <NamedLayer>
        <Name>${sldName}</Name>
        <UserStyle>
            <Name>${sldName}</Name>
            <Title>${sldName} distribution</Title>
            <FeatureTypeStyle>
                <Rule>
                    <RasterSymbolizer>
                    <Opacity>1.0</Opacity>
                    <ColorMap type="ramp">
                        ${cmStr}
                    </ColorMap>
                    </RasterSymbolizer>
                </Rule>
            </FeatureTypeStyle>
        </UserStyle>
    </NamedLayer>
</StyledLayerDescriptor>
`;
}

const addSlds = async () => {
    const tasks = []
    for(let coverageStoreName of Object.keys(coverageStoreNames)) {
        for(let col of coverageStoreNames[coverageStoreName]) {
            if(col.min != null && col.max != null) {
                tasks.push([coverageStoreName, col.id, col.min, col.max])
            }
        }
    }
    return Bluebird.map(tasks, task => {
        return new Bluebird((resolve, reject) => {
            addSld(...task).then(res => resolve()).catch(e => resolve())
        })
    }, {
        concurrency: 10
    })
}

const addSld = async (coverageStoreName, colName, min, max) => {
    const sldName = `${coverageStoreName}-${colName}`
    const cmName = sldName
    const noDataVs = [0]
    const colors = [
        '#B8B8B8',
        '#615EFE',
        '#0080AC',
        '#01B251',
        '#73C605',
        '#DEF103',
        '#FF9703',
        '#FC0101',
        '#B30404',
    ]
    const sldBody = CM_Gemerator(sldName, cmName, min, max, noDataVs, colors)
    const url = `${setting.domain}/geoserver/rest/workspaces/Carbon_Cycle/styles`
    return requestAsync({
        url,
        method: 'POST',
        headers: {
            'content-type': 'application/vnd.ogc.sld+xml',
            Authorization: 'Basic YWRtaW46Z2Vvc2VydmVy'
        },
        body: sldBody,
    })
}

const updateSld = async (coverageStoreName, colName, min, max) => {
    const sldName = `${coverageStoreName}-${colName}`
    const cmName = sldName
    const noDataVs = [0]
    const colors = [
        '#B8B8B8',
        '#615EFE',
        '#0080AC',
        '#01B251',
        '#73C605',
        '#DEF103',
        '#FF9703',
        '#FC0101',
        '#B30404',
    ]
    const sldBody = CM_Gemerator(sldName, cmName, min, max, noDataVs, colors)
    const url = `${setting.domain}/geoserver/rest/workspaces/Carbon_Cycle/styles/${sldName}`
    return requestAsync({
        url,
        method: 'PUT',
        headers: {
            'content-type': 'application/vnd.ogc.sld+xml',
            Authorization: 'Basic YWRtaW46Z2Vvc2VydmVy'
        },
        body: sldBody,
    })
}

const addPointSld = async () => {
    const pointSlds = [
`<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0"
xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd" xmlns="http://www.opengis.net/sld"
xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<NamedLayer>
    <Name>obs-site</Name>
    <UserStyle>
    <Name>obs-site</Name>
    <Title>Capital cities</Title>
    <FeatureTypeStyle>
        <Rule>
        <Title>Capitals</Title>
        <PointSymbolizer>
            <Graphic>
            <Mark>
                <WellKnownName>circle</WellKnownName>
                <Fill>
                <CssParameter name="fill">
                    <ogc:Literal>#FFFFFF</ogc:Literal>
                </CssParameter>
                </Fill>
                <Stroke>
                <CssParameter name="stroke">
                    <ogc:Literal>#0000FF</ogc:Literal>
                </CssParameter>
                <CssParameter name="stroke-width">
                    <ogc:Literal>2</ogc:Literal>
                </CssParameter>
                </Stroke>
            </Mark>
            <Opacity>
                <ogc:Literal>1.0</ogc:Literal>
            </Opacity>
            <Size>
                <ogc:Literal>6</ogc:Literal>
            </Size>

            </Graphic>
        </PointSymbolizer>
        </Rule>
    </FeatureTypeStyle>
    </UserStyle>
</NamedLayer>
</StyledLayerDescriptor>`, 
`<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0" 
    xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" 
    xmlns="http://www.opengis.net/sld" 
    xmlns:ogc="http://www.opengis.net/ogc" 
    xmlns:xlink="http://www.w3.org/1999/xlink" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <NamedLayer>
    <Name>grid-site</Name>
    <UserStyle>
        <Name>grid-site</Name>
        <Title>grid-site</Title>
        <Abstract>grid-site</Abstract>
        <FeatureTypeStyle>
        <Rule>
            <Name>grid-site</Name>
            <Title>Blue Square</Title>
            <PointSymbolizer>
                <Graphic>
                <Mark>
                    <WellKnownName>square</WellKnownName>
                    <Fill>
                    <CssParameter name="fill">#0099FF</CssParameter>
                    </Fill>
                </Mark>
                <Size>6</Size>
            </Graphic>
            </PointSymbolizer>
        </Rule>
        </FeatureTypeStyle>
    </UserStyle>
    </NamedLayer>
</StyledLayerDescriptor>`
    ]
    return Bluebird.map(pointSlds, sld => {
        requestAsync({
            url: `${setting.domain}/geoserver/rest/workspaces/Carbon_Cycle/styles`,
            method: 'POST',
            headers: {
                'content-type': 'application/vnd.ogc.sld+xml',
                Authorization: 'Basic YWRtaW46Z2Vvc2VydmVy'
            },
            body: sld,
        })
    })
}

const removeAllWorkspaceSlds = async () => {
    requestAsync({
        url: ``
    })
}

module.exports = async () => {
    await addSlds()
    await addPointSld()
}

// const main = async () => {
//     // await addSld('IBIS-avg', 'adaet', 0, 5.6, )
//     await addSlds()
// }

// main()
//     .then(() => {
//         console.log('finished!')
//         process.exit(0)
//     })
//     .catch(e => {
//         console.error(e)
//         process.exit(1)
//     })
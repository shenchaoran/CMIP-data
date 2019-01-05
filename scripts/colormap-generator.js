// https://www.npmjs.com/package/colormap

const colormap = require('colormap')
const cmGemerator = (sldName, cmName, min, max, count, noDataVs) => {
    let colors = colormap({
        colormap: cmName,
        nshades: count,
        format: 'hex',
        alpha: 1
    })
    let cmStr = '';
    let delta = (max - min)/ count;
    for(let i=0; i< count; i++) {
        let quantity = delta * i + min
        cmStr += `<ColorMapEntry color="${colors[i]}" quantity="${quantity}" />\n`
    }
    if(noDataVs)
        noDataVs.map(noDataV => {
            cmStr += `<ColorMapEntry color="#fff" quantity="${noDataV}" opacity="0" />\n`
        })
    return `<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0" xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc"
    xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
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
            <ColorMap>
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

// let rst = cmGemerator('hsv', 0, 10, 100, 11)
let gppSLD = cmGemerator('annual GPP', 'hsv', 0, 3650, 100, [0, -99999])
let nppSLD = cmGemerator('annual NPP', 'hsv', 0, 3650, 100, [0, -99999])
let nepSLD = cmGemerator('annual NEP', 'hsv', -3650, 3650, 100, [0, -99999])
let neeSLD = cmGemerator('annual NEE', 'hsv', -3650, 3650, 100, [0, -99999])
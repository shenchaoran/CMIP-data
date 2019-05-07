const sldFn = require('./sld')
const coverageStoreFn = require('./coverage-store')
const dataStoreFn = require('./data-store')
const layerFn = require('./layers')
const wsFn = require('./workspace')

const main = async () => {
    await wsFn()
    await sldFn()
    await coverageStoreFn()
    await dataStoreFn()
    await layerFn()
}

main()
    .then(() => {
        console.log('finished!')
        process.exit(0)
    })
    .catch(e => {
        console.error(e)
        process.exit(1)
    })
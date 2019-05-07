const setting = require('./setting')
const request = require('request')
const requestAsync = require('request-promise')
const Bluebird = require('bluebird')
const fs = require('fs')

const addWs = async () => {
    const url = `${setting.domain}/geoserver/rest/workspaces`
    return requestAsync({
        url,
        method: 'POST',
        headers: {
            'content-type': 'application/json',
            Authorization: 'Basic YWRtaW46Z2Vvc2VydmVy'
        },
        json: true,
        body: {
            workspace: { name: 'Carbon_Cycle' }
        }
    })
}

const deleteWs = async () => {
    const url = `${setting.domain}/geoserver/rest/workspaces/Carbon_Cycle?recurse=true`
    return requestAsync({
        url,
        method: 'DELETE',
        headers: {
            Authorization: 'Basic YWRtaW46Z2Vvc2VydmVy'
        },
    })
}

const resetWs = async () => {
    await deleteWs()
    await addWs()
    return
}

module.exports = resetWs
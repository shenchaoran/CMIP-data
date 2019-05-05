const mongoose  = require('mongoose')
const Bluebird = require('bluebird')


mongoose.Promise = Bluebird
mongoose.set('debug', true)
mongoose.connect('mongodb://223.2.35.73:27017/Comparison')
mongoose.connection.on('connected' () => {
    console.log('Mongoose connected')
})
mongoose.connection.on('error' (err) => {
    console.error('Mongoose err', err)
})
mongoose.connection.on('disconnected' () => {
    console.log('Mongoose disconnected')
})

const slns = [
    '5c3be0f7896f318e14000053',
    '5c3c70613139ed0427000004',
    '5c3c87243139ed0427000030',
]

var Schema = mongoose.Schema
var SiteSchema = new Schema({
    id: String,
    lat: Number,
    long: Number,
    name: String,
    url: String,
    startTime: Number,
    endTime: Number,
    index: Number,
})
var Site = mongoose.model('Site', SiteSchema)
Site.find({}, (err, docs) => {
    if(err) {
        err
    }
    else {
        docs;
        
    }
})
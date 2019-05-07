const requestPromise = require('request-promise');
const request = require('request');
const fs = require('fs')
const Bluebird = require('bluebird')
const http = require('http')
const path = require('path')
const mongodb = require('mongodb')
const ObjectId = mongodb.ObjectID
const EventEmitter = require('events')

// reference: https://github.com/request/request-promise

export const getByServer = (url, form, isFullResponse) => {
    const options = {
        url: url,
        method: 'GET',
        qs: form,
        resolveWithFullResponse: isFullResponse === true
        // proxy: "http://127.0.0.1:3122"//for fiddler
    };
    return requestPromise(options)
        .catch(e => {
            return Bluebird.reject(e)
        })
};

export const postByServer = (url, body, type) => {
    const options = {
        uri: url,
        method: 'POST'
    };
    if (type === 'JSON') {
        // 后台信息都会存在req.body中
        options.body = body;
        // must add this line
        // encode the body to stringified json
        options.json = true;
        // Is set automatically
        options.headers = {
            'content-type': 'application/json'
        };
    } else if (type === 'Form') {
        // 后台会全部放在req.body中。
        // 所以如果有文件的话，不能放在form中，headers不能为urlencoded
        options.form = body;
        // Is set automatically
        options.headers = {
            'content-type': 'application/x-www-form-urlencoded'
        };
    } else if (type === 'File') {
        // 后台不在req.body, req.params, req.query中。
        // 所以如果在req.query中取值，要把那部分单独拿出来，插入到url中
        options.formData = body;
        // Is set automatically
        options.headers = {
            'content-type': 'multipart/form-data'
        };
    }
    return requestPromise(options)
        .catch(e => {
            return Bluebird.reject(e)
        })
};

// 通过管道请求转发 TODO fix hot
export const getByPipe = (req, url) => {
    return new Bluebird((resolve, reject) => {
        req.pipe(
            request.get(url, (err, response, body) => {
                if (err) {
                    return reject(err);
                } else {
                    return resolve({
                        response: response,
                        body: body
                    });
                }
            })
        );
    });
};

export const postByPipe = (req, url) => {
    return new Bluebird((resolve, reject) => {
        req.pipe(
            request
                .post(url)
                .then(response => {
                    return resolve(response);
                })
                .catch(error => {
                    return reject(error);
                })
        );
    });
};

/**
 * @return {stream, fname}
 * 
 * 从远程请求文件，将文件写到本地，并将响应流返回到前台
 * fn 是写完文件后执行的函数，不是回调
 */
export const getFile = async (url, folder) => {
    try {
        const fetchEvent = new EventEmitter();
        let fname, fpath, newName
        newName = new ObjectID().toString()
        http.get(url, stream => {
            // let res$1, res$2
            // res$1 = new PassThrough()
            // res$2 = new PassThrough()
            // response.pipe(res$1)
            // response.pipe(res$2)

            fname = stream.headers['content-disposition'];
            if (fname && fname.indexOf('filename=') !== -1)
                fname = fname.substring(fname.indexOf('filename=') + 9);
            if (!fname)
                fname = new ObjectID().toString();
            if (fname.lastIndexOf('.') !== -1) 
                newName += fname.substr(fname.lastIndexOf('.'))
            fpath = path.join(folder, newName)

            fetchEvent.emit('response', {
                stream,
                fname
            })

            // TODO some file download don't enter here???
            stream.pipe(fs.createWriteStream(fpath))
            stream.on('end', chunk => {
                fetchEvent.emit('afterWrite', {
                    fname,
                    fpath: newName
                })
            })
        })
        return fetchEvent;
    }
    catch (e) {
        return Bluebird.reject(e)
    }
}

// export enum PostRequestType {
//     // JSON REST API
//     JSON = 1,
//     // POST like a form
//     Form = 2,
//     // contains file
//     File = 3
// }

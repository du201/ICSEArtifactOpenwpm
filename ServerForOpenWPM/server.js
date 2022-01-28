const express = require('express')
const app = express()
const cors = require('cors')
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
var fs = require('fs');
const { logTrackSchema, triggeredFuncSchema, onSubmitSchema, onAttemptedSubmitSchema, patternAttributesSchema, usedStringSchema, formNumSchema } = require('./mongooseSchema');
const port = 3050
const { POSIX, MONGODB } = require('./constant.js');

app.use(cors())
app.use(express.json({ limit: '50mb' }));
// app.use(express.urlencoded({ limit: '50mb' }));

store().catch(error => {
    console.log("Error in store()!: \n" + error.stack);
});

let isBlocking = false;
let debug = false;
let outputString = '';

if (process.argv[2]) {
    if (process.argv[2] === "--debug") {
        debug = true;
        console.log("debug output enabled");
    }
}

// do not perform file IO in request handler. It would trigger page reload. I don't know why!

async function store() {
    const uri = MONGODB;
    await mongoose.connect(uri, { useNewUrlParser: true, useUnifiedTopology: true });

    const triggered_func = mongoose.model(`triggered_func${POSIX}`, triggeredFuncSchema);
    const on_submit = mongoose.model(`on_submit${POSIX}`, onSubmitSchema);
    const used_string = mongoose.model(`used_string${POSIX}`, usedStringSchema);
    const pattern_attribute = mongoose.model(`pattern_attribute${POSIX}`, patternAttributesSchema);
    const form_num = mongoose.model(`form_num${POSIX}`, formNumSchema);
    const log_track = mongoose.model(`log_track${POSIX}`, logTrackSchema);

    app.get('/', (req, res) => {
        console.log('Form submission received')
        if (debug) {
            outputString += 'Form submission received' + '\n';
        }
        res.send('Hello World!')
    })

    app.post('/triggered_func', function (req, res) {
        console.log('triggered_func request received')
        // req.body is a JavaScript Object

        let promise = triggered_func.create(req.body);
        promise.catch((error) => {
            fs.appendFile('error.log', `${error.toString()}`, (err) => {
                if (err) throw err;
            });
        });

        if (debug) {
            console.log(JSON.stringify(req.body))
            outputString += 'triggered_func request received\n';
            outputString += JSON.stringify(req.body) + '\n';
        }

        res.send('triggered_func request finished')
    })

    app.post('/on_submit', function (req, res) {
        console.log('on_submit request received')
        // req.body is a JavaScript Object

        let promise = on_submit.create(req.body);

        if (debug) {
            console.log(JSON.stringify(req.body))
            outputString += 'on_submit request received\n';
            outputString += JSON.stringify(req.body) + '\n';
        }

        res.send('on_submit request finished')
    })

    app.post('/pattern_attribute', function (req, res) {
        console.log('pattern_attribute request received')
        // req.body is a JavaScript Object

        let promise = pattern_attribute.create(req.body);

        if (debug) {
            console.log(JSON.stringify(req.body))
            outputString += 'pattern_attribute request received\n';
            outputString += JSON.stringify(req.body) + '\n';
        }

        res.send('pattern_attribute request finished')
    })

    app.post('/form_num_count', function (req, res) {
        console.log('form_num_count request received')
        // req.body is a JavaScript Object

        let promise = form_num.create(req.body);

        if (debug) {
            console.log(JSON.stringify(req.body))
            outputString += 'form_num_count request received\n';
            outputString += JSON.stringify(req.body) + '\n';
        }

        res.send('form_num_count request finished')
    })

    app.post('/used_string', function (req, res) {
        console.log('used_string request received')
        // req.body is a JavaScript Object

        let promise = used_string.create(req.body);

        if (debug) {
            console.log(JSON.stringify(req.body));
            outputString += 'used_string request received\n';
            outputString += JSON.stringify(req.body) + '\n';
        }

        res.send('used_string request finished')
    })

    app.post('/log_track', function (req, res) {
        let promise = log_track.create(req.body);
        console.log('log_track request received')
        res.send('log_track request finished')
    })


    // app.get('/start-blocking', (req, res) => {
    //     console.log('start-blocking')
    //     isBlocking = true;
    //     setTimeout(function () {
    //         isBlocking = false;
    //         console.log('stop-blocking')
    //     }, 3000);
    //     res.send('');
    // })

    // app.get('/stop-blocking', (req, res) => {
    //     console.log('stop-blocking')
    //     isBlocking = false;
    //     res.send('');
    // })

    // app.get('/is-blocking', (req, res) => {
    //     res.send({ isBlocking });
    // })

    // app.post('/log', async function (req, res) {
    //     console.log('POST request received')
    //     // req.body is a JavaScript Object
    //     console.log(req.body)

    //     //await model.create({ webpage_url: req.body.url, regex: req.body.regex, typed_string: req.body.string, triggered_func: req.body.funcName, time: req.body.time, domain: req.body.host });

    //     res.send('POST request received')
    // })

    app.post('/', async function (req, res) {
        console.log('POST request received from the test webpage')
        // req.body is a JavaScript Object
        console.log(req.body)

        // await model.create({ webpage_url: req.body.url, regex: req.body.regex, typed_string: req.body.string, triggered_func: req.body.funcName, time: req.body.time, domain: req.body.host });

        res.send('POST request received')
    })

    app.listen(port, () => {
        console.log(`Example app listening at http://localhost:${port}`)
    })
}

process.on('SIGINT', () => {
    console.log('You clicked Ctrl+C!');
    fs.writeFileSync('testResult.txt', outputString);
    process.exit(1);
});
const express = require('express')
const app = express()
const cors = require('cors')
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
var fs = require('fs');
const { triggeredFuncSchema, onSubmitSchema, usedStringSchema, analyzeTriggeredFuncSchema, formNumSchema, patternAttributesSchema, logTrackSchema } = require('../mongooseSchema');
const port = 3050
const { POSIX, MONGODB } = require('../constant.js');

app.use(cors())
app.use(express.json());

store().catch(error => {
    console.log("Error in store()!: \n" + error.stack);
});

let isBlocking = false;
let debug = false;
let outputString = '';


async function store() {
    const uri = MONGODB;
    await mongoose.connect(uri, { useNewUrlParser: true, useUnifiedTopology: true });

    const triggered_func = mongoose.model(`triggered_func${POSIX}`, triggeredFuncSchema);
    const on_submit = mongoose.model(`on_submit${POSIX}`, onSubmitSchema);
    const used_string = mongoose.model(`used_string${POSIX}`, usedStringSchema);
    const analyze_triggered_func = mongoose.model(`analyze_triggered_func${POSIX}`, analyzeTriggeredFuncSchema);
    const form_num = mongoose.model(`form_num${POSIX}`, formNumSchema);
    const pattern_attribute = mongoose.model(`pattern_attribute${POSIX}`, patternAttributesSchema);
    const log_track = mongoose.model(`log_track${POSIX}`, logTrackSchema);

    await triggered_func.deleteMany({});
    await on_submit.deleteMany({});
    await used_string.deleteMany({});
    await analyze_triggered_func.deleteMany({});
    await form_num.deleteMany({});
    await pattern_attribute.deleteMany({});
    await log_track.deleteMany({});

    console.log('done');
}
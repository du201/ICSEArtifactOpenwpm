const express = require('express')
const app = express()
const cors = require('cors')
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
var fs = require('fs');
const { triggeredFuncSchema, onSubmitSchema, usedStringSchema, analyzeTriggeredFuncSchema, formNumSchema, patternAttributesSchema } = require('../mongooseSchema');
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

    const pattern_attribute = mongoose.model(`pattern_attribute${POSIX}`, patternAttributesSchema);

    let docs = await pattern_attribute.find();

    let numPatterns = 0;
    let count = 0;
    let patternAttributeObjs = [];
    let patternAttributeUniqueObjs = [];

    for (let doc of docs) {
        if (doc.pattern_input.length > 0) {
            numPatterns += doc.pattern_input.length;
            let obj = doc.toObject();
            for (let pattern_abbribute of obj.pattern_input) {
                pattern_abbribute['has_scanned'] = false;
                pattern_abbribute['is_vulnerable'] = false;
            }
            patternAttributeObjs.push(obj);
        }
    }

    console.log(`There are ${numPatterns} pattern attributes`);
    fs.writeFileSync('patternAttributeObjs.json', JSON.stringify(patternAttributeObjs));

    let unique = new Set();
    for (let obj of patternAttributeObjs) {
        for (let pattern of obj.pattern_input) {
            if (!unique.has(pattern.pattern)) {
                patternAttributeUniqueObjs.push(obj);
                unique.add(pattern.pattern);
            }
        }
    }

    console.log(`of which ${unique.size} are unique`);
    fs.writeFileSync('uniquePattern.json', JSON.stringify(Array.from(unique)))

    await mongoose.disconnect();
    console.log('done!');
}
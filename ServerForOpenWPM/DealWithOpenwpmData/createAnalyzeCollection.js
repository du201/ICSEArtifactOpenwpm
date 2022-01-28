const mongoose = require('mongoose');
var fs = require('fs');
const { triggeredFuncSchema, onSubmitSchema, onAttemptedSubmitSchema, usedStringSchema, analyzeTriggeredFuncSchema } = require('../mongooseSchema');
const { POSIX, MONGODB } = require('../constant.js');

store().catch(error => {
    console.log("Error in store()!: \n" + error.stack);
});

async function store() {
    const uri = MONGODB;
    await mongoose.connect(uri, { useNewUrlParser: true, useUnifiedTopology: true });

    const triggered_func = mongoose.model(`triggered_func${POSIX}`, triggeredFuncSchema);

    const analyze_triggered_func = mongoose.model(`analyze_triggered_func${POSIX}`, analyzeTriggeredFuncSchema);

    await analyze_triggered_func.deleteMany({});

    let interestingDocs = await triggered_func.find();

    for (let doc of interestingDocs) {
        await analyze_triggered_func.create(
            {
                page_url: doc.page_url, regex: doc.regex, used_string: doc.used_string,
                triggered_func: doc.triggered_func, timestamp: doc.timestamp, domain: doc.domain,
                is_vulnerable: false, has_scanned: false, ith_form: doc.ith_form
            });
    }

    await mongoose.disconnect();
    console.log('done!');
}

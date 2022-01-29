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

    const on_submit = mongoose.model(`on_submit${POSIX}`, triggeredFuncSchema);
    const analyze_triggered_func = mongoose.model(`analyze_triggered_func${POSIX}`, analyzeTriggeredFuncSchema);
    const used_string = mongoose.model(`used_string${POSIX}`, usedStringSchema);

    let onSubmitDocs = await on_submit.find();
    let analyzeTriggeredFuncDocs = await analyze_triggered_func.find();
    let usedStringDocs = await used_string.find();

    let vulnPatternObjs = JSON.parse(fs.readFileSync('vulnPatternAttributeObjs.json'));
    let uniqueVulnPatternSet = new Set();
    let uniqueUrlSet = new Set();
    let pairsOfOnSubmitAndVulnPattern = [];
    for (let vulnPatternObj of vulnPatternObjs) {

        uniqueVulnPatternSet.add(vulnPatternObj.regex)
        for (let onSubmitDoc of onSubmitDocs) {

            if (onSubmitDoc.page_url == vulnPatternObj.page_url && onSubmitDoc.ith_form == vulnPatternObj.ith_form) {
                let onSubmitObj = onSubmitDoc.toObject()
                uniqueUrlSet.add(onSubmitDoc.page_url);
                pairsOfOnSubmitAndVulnPattern.push({ vulnPatternObj, onSubmitObj });
            }
        }
    }
    console.log(`There are ${uniqueVulnPatternSet.size} unique vuln patterns`);
    fs.writeFileSync('uniqueVulnPatternSet.json', JSON.stringify(Array.from(uniqueVulnPatternSet)));
    console.log(`There are ${pairsOfOnSubmitAndVulnPattern.length} on_submit docs related`);
    fs.writeFileSync('pairsOfOnSubmitAndVulnPattern.json', JSON.stringify(Array.from(pairsOfOnSubmitAndVulnPattern)));

    // filter out those analyzeTriggeredFuncDocs that are vulnerable
    let vulnRegexObjs = [];
    let uniqueRegexSet = new Set();
    let uniqueVulnRegexSet = new Set();
    for (let analyzeTriggeredFuncDoc of analyzeTriggeredFuncDocs) {
        uniqueRegexSet.add(analyzeTriggeredFuncDoc.regex);
        if (analyzeTriggeredFuncDoc.is_vulnerable) {
            uniqueVulnRegexSet.add(analyzeTriggeredFuncDoc.regex)
            let obj = analyzeTriggeredFuncDoc.toObject();
            obj['is_pattern_attribute'] = false;
            vulnRegexObjs.push(obj);
        }
    }

    console.log(`There are ${uniqueRegexSet.size} unique regexes from JS instrumentation`);
    fs.writeFileSync('uniqueRegexSet.json', JSON.stringify(Array.from(uniqueRegexSet)));
    fs.writeFileSync('uniqueVulnRegexSet.json', JSON.stringify(Array.from(uniqueVulnRegexSet)));

    console.log(`There are ${vulnRegexObjs.length} vulnerable regexes from JS instrumentation, of which ${uniqueVulnRegexSet.size} are unique`);
    fs.writeFileSync('vulnRegexObjs.json', JSON.stringify(vulnRegexObjs));

    let pairsOfOnSubmitAndVulnRegex = [];
    for (let vulnRegexObj of vulnRegexObjs) {

        for (let usedStringDoc of usedStringDocs) {
            if (usedStringDoc.page_url == vulnRegexObj.page_url && usedStringDoc.ith_form == vulnRegexObj.ith_form) {
                let usedStringObj = usedStringDoc.toObject();

                console.log(usedStringObj.used_string.includes(vulnRegexObj.used_string)); // the result of this should always be true

                if (!usedStringObj.used_string.includes(vulnRegexObj.used_string)) {
                    console.log('Error occurred!');
                    console.log(vulnRegexObj);
                }
            }
        }

        for (let onSubmitDoc of onSubmitDocs) {
            if (onSubmitDoc.page_url == vulnRegexObj.page_url && onSubmitDoc.ith_form == vulnRegexObj.ith_form) {
                let onSubmitObj = onSubmitDoc.toObject()
                pairsOfOnSubmitAndVulnRegex.push({ vulnRegexObj, onSubmitObj });
                uniqueUrlSet.add(onSubmitDoc.page_url);
            }
        }
    }

    console.log(`There are ${pairsOfOnSubmitAndVulnRegex.length} on_submit docs related`);
    console.log(`There are ${uniqueUrlSet.size} web pages related`);
    fs.writeFileSync('pairsOfOnSubmitAndVulnRegex.json', JSON.stringify(pairsOfOnSubmitAndVulnRegex));
    await mongoose.disconnect();
    console.log('finished');
}

const mongoose = require('mongoose');
var fs = require('fs');
const yaml = require('js-yaml');
const { triggeredFuncSchema, onSubmitSchema, onAttemptedSubmitSchema, usedStringSchema, analyzeTriggeredFuncSchema } = require('../mongooseSchema');
const { POSIX, MONGODB } = require('../constant.js');
let openAPINum = 0;
let totalNum = 0;

store().catch(error => {
    console.log("Error in store()!: \n" + error.stack);
});

async function store() {
    const uri = MONGODB;

    let urlSet = new Set();
    let pairsOfOnSubmitAndVulnRegex = JSON.parse(fs.readFileSync('pairsOfOnSubmitAndVulnRegex.json'));
    let pairsOfOnSubmitAndVulnPattern = JSON.parse(fs.readFileSync('pairsOfOnSubmitAndVulnPattern.json'));

    for (let { vulnRegexObj, onSubmitObj } of pairsOfOnSubmitAndVulnRegex) {
        totalNum++;
        urlSet.add(onSubmitObj.page_url);
        generateOpenAPI(vulnRegexObj, onSubmitObj, false);
    }
    console.log(`For regex from JS, out of ${totalNum} pairs, ${openAPINum} can be generated as OpenAPI docs`);
    totalNum = 0;
    openAPINum = 0;

    for (let { vulnPatternObj, onSubmitObj } of pairsOfOnSubmitAndVulnPattern) {
        totalNum++;
        urlSet.add(onSubmitObj.page_url);
        generateOpenAPI(vulnPatternObj, onSubmitObj, true);
    }
    console.log(`For patterns, out of ${totalNum} pairs, ${openAPINum} can be generated as OpenAPI docs`);
    console.log(`We have ${urlSet.size} urls related`);
    // await mongoose.disconnect();
    console.log('finishes');
}

function generateOpenAPI(vulnRegexObj, onSubmitObj, isPattern) {

    let openAPIInfo = JSON.parse(onSubmitObj.openAPI);
    let properties = {};
    let match = false;

    for (let input of openAPIInfo.inputs) {
        properties[input.name] = { default: input.value };
    }

    for (let select of openAPIInfo.selects) {
        properties[select.name] = { default: select.values.length != 0 ? select.values[0] : 'random choice' };
    }

    for (let textarea of openAPIInfo.textareas) {
        properties[textarea.name] = { default: 'hello' };
    }

    for (const [key, value] of Object.entries(properties)) {
        if (vulnRegexObj.is_pattern_attribute) {
            if (vulnRegexObj.name != "" && vulnRegexObj.name == key) {
                openAPINum++;
                properties[key]['type'] = 'string';
                properties[key]['pattern'] = vulnRegexObj.regex;
                delete properties[key]['default'];
                match = true;
                break;
            } else if (value.default == vulnRegexObj.used_string) {
                openAPINum++;
                properties[key]['type'] = 'string';
                properties[key]['pattern'] = vulnRegexObj.regex;
                delete properties[key]['default'];
                match = true;
                break;
            }
        } else {
            if (value.default == vulnRegexObj.used_string) {
                openAPINum++;
                properties[key]['type'] = 'string';
                properties[key]['pattern'] = vulnRegexObj.regex;
                delete properties[key]['default'];
                match = true;
                break;
            }
        }
    }

    if (match) {
        let myURL = new URL(openAPIInfo.action);
        let serverURL = myURL.origin;
        let pathURL = myURL.pathname;

        let openAPIOutput = {
            info: {
                title: "a form based OpenAPI doc",
                version: '1.0.0'
            },
            openapi: '3.0.0',
            paths: {},
            servers: [{ url: serverURL }]
        };

        let responses = {
            '200': {
                description: 'OK'
            }
        };

        if (openAPIInfo.method == "post") {

            let requestBody = {
                required: true,
                content: {
                    'application/x-www-form-urlencoded': {
                        schema: {
                            properties: properties,
                            type: 'object'
                        }
                    }
                }
            };

            openAPIOutput.paths[pathURL] = {
                post: {
                    requestBody: requestBody,
                    responses: responses,
                    summary: 'a form based OpenAPI Doc'
                }
            };

        } else if (openAPIInfo.method == "get") {
            let parameters = [];

            for (const [key, value] of Object.entries(properties)) {
                parameters.push({ in: 'query', name: key, required: true, schema: value });
            }

            openAPIOutput.paths[pathURL] = {
                get: {
                    parameters: parameters,
                    responses: responses,
                    summary: 'a form based OpenAPI Doc'
                }
            };
        }

        fs.writeFileSync(`${process.env.HOME}/${process.env.API_DIR}/openAPI_${isPattern ? 'pattern' : 'regex'}_${openAPINum}.yaml`, yaml.dump(openAPIOutput, {
            'styles': {
                '!!null': 'canonical'
            },
            'sortKeys': true
        }));
    }
}

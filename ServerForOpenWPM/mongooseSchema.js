const mongoose = require('mongoose');

module.exports.triggeredFuncSchema = new mongoose.Schema(
    [{ page_url: String, regex: String, used_string: String, triggered_func: String, timestamp: String, domain: String, ith_form: Number }]);

module.exports.analyzeTriggeredFuncSchema = new mongoose.Schema(
    [{ page_url: String, regex: String, used_string: String, triggered_func: String, timestamp: String, domain: String, is_vulnerable: Boolean, has_scanned: Boolean, ith_form: Number }]);

module.exports.onSubmitSchema = new mongoose.Schema(
    { openAPI: String, page_url: String, is_successful_submit: Boolean, ith_form: Number });

module.exports.usedStringSchema = new mongoose.Schema(
    { page_url: String, used_string: [String], ith_form: Number });

module.exports.logTrackSchema = new mongoose.Schema(
    { page_url: String, is_successful: Boolean, timestamp: String, ith_start: Number, ith_end: Number });

module.exports.patternAttributesSchema = new mongoose.Schema(
    { page_url: String, pattern_input: [{ pattern: String, has_input_text: Boolean, used_string: String, name: String }], ith_form: Number });

module.exports.formNumSchema = new mongoose.Schema(
    { page_url: String, num_form: Number });
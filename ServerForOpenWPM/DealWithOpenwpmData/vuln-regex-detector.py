import os
from typing import Optional, Pattern, Union, Tuple, List
import re
import subprocess
import json
from pymongo import MongoClient
import datetime

# regex: a string of the regex
def AnalyzeRegex(regex):

    ''' Given a regex, returns an attack string schema if it is vulnerable.
    '''
    time_limit = 1
    with open(f"{os.environ['VULN_REGEX_DETECTOR_ROOT']}/bin/tmp.json", "w") as f:
        config_dict = dict(pattern=regex,validateVuln_language="javascript",validateVuln_timeLimit=time_limit)
        json.dump(config_dict, f)
    
    my_env = os.environ.copy()
    # my_env['VULN_REGEX_DETECTOR_ROOT']="/home/efe/vuln-regex-detector" #FIXME
    result = subprocess.run("cd $VULN_REGEX_DETECTOR_ROOT; \
                            cd bin; \
                            ./check-regex.pl tmp.json", shell=True, env=my_env, capture_output=True)
    match = re.search('{.*}', result.stdout.decode("utf-8"))
    if match is None:
        return None

    json_str = match.group(0)
    report = json.loads(json_str)
    
    '''
    with open("tmp", "w") as f:
        json.dump(report, f)
    return report
    '''
    
    return report


POSIX = '_test3'

client = MongoClient("mongodb+srv://xin:20000114@cluster0.zvpso.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
                 
analyze_triggered_funcs = client['regex'][f'analyze_triggered_func{POSIX}']
docs = analyze_triggered_funcs.find({})
doc_count = 0
for doc in docs:
    doc_count += 1
    file1 = open("timeLog", "a")  # append mode
    file1.write(f"Function vuln-regex-detect.py starts the {doc_count}th doc at {datetime.datetime.now()}\n")
    file1.close()
    if (not doc['has_scanned']): 
        # https://stackoverflow.com/questions/522563/accessing-the-index-in-for-loops
        # doc['regexes'] could be a 0-length list, but that won't cause any exception
        regex = doc['regex']
        report = AnalyzeRegex(regex)
        if (report['isVulnerable'] == 1):
            analyze_triggered_funcs.update_one(
                {"_id":doc['_id']},
                {"$set": {f"is_vulnerable": True, f"has_scanned": True}})

        analyze_triggered_funcs.update_one(
            {"_id":doc['_id']},
            {"$set": {f"has_scanned": True}})

f = open('patternAttributeObjs.json',)
patternAttributeObjs = json.load(f)
vulnPatternAttributeObjs = []
doc_count = 0
# print(patterns)
for patternAttributeObj in patternAttributeObjs:
    for pattern_input in patternAttributeObj['pattern_input']:
        doc_count += 1
        file1 = open("timeLog", "a")  # append mode
        file1.write(f"Function vuln-regex-detect.py starts the {doc_count}th pattern at {datetime.datetime.now()}\n")
        file1.close()
        report = AnalyzeRegex(pattern_input['pattern'])
        pattern_input['has_scanned'] = True
        if (report['isVulnerable'] == 1):
            print(f'vulnerable! It is {pattern_input["pattern"]}')
            pattern_input['is_vulnerable'] = True
            vulnPatternAttributeObjs.append(
                {"page_url": patternAttributeObj['page_url'], 
                "ith_form": patternAttributeObj['ith_form'],
                "regex": pattern_input['pattern'],
                "has_input_text": pattern_input['has_input_text'],
                "used_string": pattern_input['used_string'],
                "name": pattern_input['name'],
                "is_pattern_attribute": True})

with open('patternAttributeObjs.json', 'w') as f:
    json.dump(patternAttributeObjs, f)
with open('vulnPatternAttributeObjs.json', 'w') as f:
    json.dump(vulnPatternAttributeObjs, f)

file1 = open("timeLog", "a")  # append mode
file1.write(f"Function vuln-regex-detect.py finishes at {datetime.datetime.now()}\n")
file1.close()   
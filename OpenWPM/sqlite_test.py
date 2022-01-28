import sqlite3
import json
import yaml
from urllib.parse import urlparse

openAPI_obj = {
    'info': {
        'title': 'The number 1 form in this url',
        'version': '1.0.0'
    },
    'openapi': '3.0.0',
    'paths': {},
    'servers': []
}

regex_field = 'Phone'
regex_pattern = '(.*\d.*){8,}'

conn = sqlite3.connect('./datadir/crawl-data.sqlite')

c = conn.cursor()

c.execute("SELECT post_body, url, headers FROM http_requests WHERE id = 3166;")

rows = c.fetchall()
# print(rows)
for row in rows:
    header_string = row[2]
    url = row[1]
    post_body_string = row[0]

    url_obj = urlparse(url)
    servers_url = url_obj.scheme + '://' + url_obj.netloc
    path = url_obj.path

    post_body_obj = json.loads(post_body_string)
    for key in post_body_obj:
        post_body_obj[key] = { 'default': post_body_obj[key][0] }

    # Modify the field that has regex
    post_body_obj[regex_field] = {
        'type': 'string',
        'pattern': regex_pattern
    }

    # Construct header parameters (for now, all headers are included)
    header = json.loads(header_string)
    openAPI_obj_header_parameters = []
    for parameter in header:
        openAPI_obj_header_parameters.append({
            'in': 'header',
            'name': parameter[0],
            'required': True,
            'schema': {
                'default': parameter[1]
            }
        })

    openAPI_obj['servers'].append({ 'url': servers_url })
    openAPI_obj['paths'][path] = {
        'post': {
            'summary': 'a form post request generated from OpenWPM',
            'requestBody': {
                'required': True,
                'content': {
                    'application/x-www-form-urlencoded': {
                        'schema': {
                            'type': 'object',
                            'properties': post_body_obj
                        }
                    }
                }
            },
            'parameters': openAPI_obj_header_parameters,
            'responses': {
                '200': {
                    'description': 'OK'
                } 
            }                    
        }
    }

c.close()

with open('trial.yaml', 'w') as stream:
    yaml.dump(openAPI_obj, stream)

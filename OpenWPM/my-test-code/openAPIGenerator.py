import yaml

open_api_dict = {
    'openapi': '3.0.0',
    'info': {
        'title': 'The number 1 form in this url',
        'version': '1.0.0'
    },
    'servers': [
        {'url': 'http://localhost:3000'} 
    ],
    'paths': {
        '/': {
            'post': {
                'summary': 'a form post request generated from OpenWPM',
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/x-www-form-urlencoded': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'name': {
                                        'type': 'string',
                                        'pattern': '[a-z]{4,8}'
                                    },
                                    'pass': {
                                        'type': 'string'
                                    }
                                },
                                'required': [
                                    'name', 'pass'
                                ]
                            }
                        }
                    }
                }                            
            }
        }
    }
}


with open(r'store_file.yaml', 'w') as file:
    documents = yaml.dump(open_api_dict, file)
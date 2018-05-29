import os
import uuid
import requests
import json
from xml.dom.minidom import parse
import xml.dom.minidom
from . import main
from common import read_file


DEV_QUERYPLAN_HEADER_CONFIG_PATH ='data/marklogic/dev_queryplan_header_config.txt'
DEV_QUERYPLAN_PARAMS_CONFIG_PATH ='data/marklogic/dev_queryplan_params_config.txt'
DEV_PHRASELIST_HEADER_CONFIG_PATH ='data/marklogic/dev_phraselist_header_config.txt'
DEV_PHRASELIST_PARAMS_CONFIG_PATH ='data/marklogic/dev_phraselist_params_config.txt'
DEV_URL = 'http://dvml77868.lexis-nexis.com:8000/qconsole/endpoints/evaler.xqy'

CERT_QUERYPLAN_HEADER_CONFIG_PATH ='data/marklogic/cert_queryplan_header_config.txt'
CERT_QUERYPLAN_PARAMS_CONFIG_PATH ='data/marklogic/cert_queryplan_params_config.txt'
CERT_PHRASELIST_HEADER_CONFIG_PATH ='data/marklogic/cert_phraselist_header_config.txt'
CERT_PHRASELIST_PARAMS_CONFIG_PATH ='data/marklogic/cert_phraselist_params_config.txt'
CERT_URL = 'http://dvml77868.lexis-nexis.com:8000/qconsole/endpoints/evaler.xqy'

INSERT_PHRASE_REQUEST_BODY_PATH ='data/marklogic/insert_phrase_request_body.txt'
INSERT_QUERYPLAN_REQUEST_BODY_PATH ='data/marklogic/insert_queryplan_request_body.txt'
INSERT_PHRASE_TEMPLATE_PATH ='data/marklogic/insert_phrase_template.txt'
INSERT_QUERYPLAN_TEMPLATE_PATH ='data/marklogic/insert_queryplan_template.txt'
COUNT_REQUEST_BODY_PATH ='data/marklogic/count_request_body.txt'

class MarkLogicDataHandler():
    def __init__(self, env, opt):
        self.env = env
        self.opt = opt

    def get_headers(self):
        headers = dict()
        if self.env == 2:
            if self.opt == 'queryplan':
                for line in read_file(os.path.join(main.root_path, CERT_QUERYPLAN_HEADER_CONFIG_PATH)).split('\r\n'):
                    index = len(line.split('=')[0])+1
                    headers[line.split('=')[0]] = line[index:]
            else:
                for line in read_file(os.path.join(main.root_path, CERT_PHRASELIST_HEADER_CONFIG_PATH)).split('\r\n'):
                    index = len(line.split('=')[0])+1
                    headers[line.split('=')[0]] = line[index:]
        else:
            if self.opt =='queryplan':
                for line in read_file(os.path.join(main.root_path, DEV_QUERYPLAN_HEADER_CONFIG_PATH)).split('\r\n'):
                    index = len(line.split('=')[0])+1
                    headers[line.split('=')[0]] = line[index:]
            else:
                for line in read_file(os.path.join(main.root_path, DEV_PHRASELIST_HEADER_CONFIG_PATH)).split('\r\n'):
                    index = len(line.split('=')[0])+1
                    headers[line.split('=')[0]] = line[index:]
                
        return headers   
    

    def get_url(self):
        param =''
        url = ''
        if self.env == 2:
            if self.opt == 'queryplan':
                param = '&'.join(read_file(os.path.join(main.root_path, CERT_QUERYPLAN_PARAMS_CONFIG_PATH)).split('\r\n'))
            else:
                param = '&'.join(read_file(os.path.join(main.root_path, CERT_PHRASELIST_PARAMS_CONFIG_PATH)).split('\r\n'))
            url = CERT_URL
        else:
            if self.opt =='queryplan':
                param = '&'.join(read_file(os.path.join(main.root_path, DEV_QUERYPLAN_PARAMS_CONFIG_PATH)).split('\r\n'))
            else:
                param = '&'.join(read_file(os.path.join(main.root_path, DEV_PHRASELIST_PARAMS_CONFIG_PATH)).split('\r\n'))
            url = DEV_URL

        url = '%s%s%s' % (url, '?', param)
        return url


    def get_params(self):
        params = dict()

        if self.env == 2:
            if self.opt == 'queryplan':
                for line in read_file(os.path.join(main.root_path, CERT_QUERYPLAN_PARAMS_CONFIG_PATH)).split('\r\n'):
                    params[line.split('=')[0]] = line.split('=')[1]
            else:
                for line in read_file(os.path.join(main.root_path, CERT_PHRASELIST_PARAMS_CONFIG_PATH)).split('\r\n'):
                    params[line.split('=')[0]] = line.split('=')[1]
        else:
            if self.opt =='queryplan':
                for line in read_file(os.path.join(main.root_path, DEV_QUERYPLAN_PARAMS_CONFIG_PATH)).split('\r\n'):
                    params[line.split('=')[0]] = line.split('=')[1]
            else:
                for line in read_file(os.path.join(main.root_path, DEV_PHRASELIST_PARAMS_CONFIG_PATH)).split('\r\n'):
                    params[line.split('=')[0]] = line.split('=')[1]

        return params  

    
    def get_insert_phrase_request_body(self):
        with open(os.path.join(main.root_path, INSERT_PHRASE_REQUEST_BODY_PATH), "r") as f:
            body = f.read()
            return body

    
    def get_insert_phrase_template(self, epoch, phraselist_name):
        with open(os.path.join(main.root_path, INSERT_PHRASE_TEMPLATE_PATH), "r") as f:
            template = f.read()
            template = template.replace('{#EpochNumber}', epoch).replace('{#PhraseListName}', phraselist_name)
            return template


    def get_insert_queryplan_request_body(self, queryplan_name):
        with open(os.path.join(main.root_path, INSERT_QUERYPLAN_REQUEST_BODY_PATH), "r") as f:
            body = f.read()
            body = body.replace('{#QueryPlanName}', queryplan_name)
            return body


    def get_insert_queryplan_template(self, hlct, phraselist_name):
        with open(os.path.join(main.root_path, INSERT_QUERYPLAN_TEMPLATE_PATH), "r") as f:
            template = f.read()
            template = template.replace('{#HLCT}', hlct).replace('{#PhraseListName}', phraselist_name)
            return template

    
    def get_count_request_body(self, epoch):
        with open(os.path.join(main.root_path, COUNT_REQUEST_BODY_PATH), "r") as f:
            body = f.read()
            body = body.replace('{#EpochNumber}', epoch)
            return body


class MarkLogicRequest(): 
    def __init__(self, headers, url, body, template):
        self.headers = headers
        self.url = url
        self.template = template
        self.body = body


    def post_insert_phrase(self, phrase_name):
        try:
            body  = self.get_phrase_body(phrase_name)        
            self.post(body)
        except Exception as e:
            print e
            return 0
        else:
            return  1
    

    def post_insert_queryplan(self):
        try:
            body  = self.get_queryplan_body()        
            print body
            self.post(body)

        except Exception as e:
            print e
            return 0
        else:
            return  1

    
    def post_delete(self, phrase_name):
        return  1

    
    def post_result(self, body):       
        response = self.post(body)
        data = json.loads(response.text)
        if data is not None:
            return int(data[0]['result'])
        return 0


    def get_phrase_body(self, phrase_name):
        key_guid = str(uuid. uuid1()).upper().replace('-','')
        second_guid = str(uuid. uuid4()).upper().replace('-','')
        template = self.template.replace('{#KeyGuid}', key_guid).replace('{#SecondGuid}', second_guid).replace('{#PhraseName}', phrase_name)
        body = self.body.replace('{#KeyGuid}', key_guid).replace('{#Doc}', template)
        return body


    def get_queryplan_body(self):
        body = self.body.replace('{#Doc}', self.template)
        return body


    def post(self, body):
        print self.url
        print self.headers
        print body
        response = requests.post(self.url, headers = self.headers, data= body)
        print response
        return response




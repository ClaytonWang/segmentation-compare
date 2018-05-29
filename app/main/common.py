import requests
import os
from . import main
import re
import datetime
import xlrd
import xlwt
import csv
from werkzeug import secure_filename

ALLOWED_EXTENSIONS = ['xls', 'xlsx', 'csv']
WAM_URL = "http://cert2-dsp:25844/8.3/services/test/wam/default.xqy?caller=search&return=&context=1000516&abtestgroup=null&abtestgroupother=z&submit=I+don%27t+have+time+for+this.&h4=Accept&v4=application%2Fatom%2Bxml&h5=&v5=&h6=&v6=&id=&pwd=&applicationpermid=1000202&endpoint=cdc2c-i-services.route53.lexis.com"
ML_URL = 'http://cdc7c-i-services.route53.lexis.com/shared/contentstore/cases-au'

def get_file_extension(filename):
    return filename.lower().split('.')[-1]


def allowed_file(filename):
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def get_filename():
    return datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')


def read_file(file_path):
    file_extention = get_file_extension(file_path)
    if file_extention == 'csv':
        return read_csv(file_path)
    elif file_extention in ['xls', 'xlsx']:
        return read_excel(file_path)
    else:
        with open(file_path, 'r') as f:
            return f.read()


def read_excel(file_path):
    excel_file = xlrd.open_workbook(file_path)
    first_sheet = excel_file.sheet_names()[0]
    sheet = excel_file.sheet_by_name(first_sheet)
    return [sheet.row_values(i) for i in range(1, sheet.nrows)]


def read_csv(file_path):
    with open(file_path, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        return [row for row in reader][1:]


def write_excel_segmentation(data, filepath):
    file = xlwt.Workbook()
    sheet = file.add_sheet('result')
    columns = [u'Query',u'Segmentation']
    for col in range(len(columns)):
        sheet.write(0,col,columns[col])

    index = 1
    for query in data:
        sheet.write(index, 0, query.body)
        sheet.write(index, 1, query.segmentation)
        index += 1

    file.save(filepath)


def write_excel(data, dic, filepath):
    file = xlwt.Workbook()
    sheet = file.add_sheet('result')
    items = [dic[key] for key in dic] 

    columns = [item[0] for item in items]
    header = [item[1] for item in items]

    for col in range(len(header)):
        sheet.write(0,col,header[col])

    index = 1
    for item in data:
        colIndex = 0
        for col in columns:
            sheet.write(index, colIndex, item[col])
            colIndex +=1
        index += 1

    file.save(filepath)


def save_file(file, folder_path):
    file_extention = get_file_extension(file.filename)
    new_filename= get_filename() + '.' + file_extention
    filepath = os.path.join(main.root_path, folder_path, new_filename)
    file.save(filepath)
    return new_filename, filepath


def unquote(str):
    str = str.replace('%253a', ':')\
        .replace("%2522", "\"")\
        .replace("%253d", "=")\
        .replace("%2b", " ")
    return str


def wam_cookies():
    cookies = dict()
    for line in read_file(os.path.join(main.root_path, 'data', 'cookies.txt')).split('\n'):
        cookies[line.split('=')[0]] = line.split('=')[1]
    return cookies


def wam():
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate',
        'authorization': 'Basic bG9hZGVyOmxvYWRlcg==',
        'Upgrade-Insecure-Requests': '1'
    }
    response = requests.get(WAM_URL, headers=headers, cookies=wam_cookies(), allow_redirects=False)
    return {
        'X-LN-Application': unquote(response.cookies['X-LN-Application']),
        'X-LN-Request': unquote(response.cookies['X-LN-Request']),
        'X-LN-Session': unquote(response.cookies['X-LN-Session'])
    }


def get_segmenation(xml):
    segmentations = []
    match = re.search(r'<parse:xmlquery[^>]*>(.*)</parse:xmlquery></search:xml-query>', xml)
    if match:
        query_str = match.group(1)
    else:
        return segmentations
    for m in re.finditer(r'<([a-z\-]+)[^>]+submittedform="([^"]+)"[^>]+>', query_str):
        query_type = m.group(1)
        token = m.group(2).replace('&quot;', '"')
        if query_type == 'proximity-query' or query_type == 'and-query' or query_type == 'or-query':
            continue
        if query_type == 'stopword-query':
            token = '[' + token + ']'
        segmentations.append(token)
    return segmentations


def segment(query, engine_id, headers):
    extra_headers = {
        'accept': 'application/atom+xml;view=la-pacific',
        'authorization': 'Basic bmV3bGV4aXM6M2FoQXhFdDg=',
        'X-LN-Sequence': '1.0',
        'X-LN-I18N': 'locale=en-AU, time-zone=US/Eastern, date-format=dd/MM/yyyy',
        'Content-Type': 'application/xml; version=2',
        'Accept-Encoding': 'gzip, deflate'
    }
    headers = dict(headers.items() + extra_headers.items())
    request_body = read_file(os.path.join(main.root_path, 'data/request', str(engine_id) + '.xml')) % query
    response = requests.post(ML_URL, headers=headers, data=request_body)
    return get_segmenation(response.text)
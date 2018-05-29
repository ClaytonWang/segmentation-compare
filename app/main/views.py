from datetime import datetime
from flask import render_template, request, redirect, url_for, make_response, send_file, flash
from . import main
from .forms import NameForm
from .. import db
from ..models import File, Query, Comparison, Marklogic, QueryPlans, Survey
from .common import allowed_file, get_file_extension, wam, segment, get_filename, read_file, write_excel_segmentation, write_excel, save_file
import json
import os
import re
from .marklogic import MarkLogicDataHandler, MarkLogicRequest


UPLOAD_FILEPATH = 'uploads'
DOWNLOAD_FILEPATH = 'downloads'
UPLOAD_COMPARISON_FILEPATH = 'uploads/comparisons'
UPLOAD_MARKLOGIC_FILEPATH = 'uploads/marklogics'

#DICTIONARY ={'[a]': 'a','[can]': 'can','[for]': 'for','[in]': 'in', '[by]':'by'}
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/surveylist',methods=['GET'])
def surveylist():
    array = []
    surveys = Survey.query.all();
    for item in surveys:
        array.append(item)
        
    return render_template('surveylist.html',surveyList = array)


@main.route('/survey/<int:svy_id>',methods=['GET'])
def survey(svy_id):
    survey = Survey.query.get(svy_id)
    svy_content = json.loads(survey.content)
    return render_template('survey.html',survey = svy_content[0])


@main.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'POST':
        querystring = request.form.get('queryString')
        engine_id = request.form.get('enginetype')
        query = Query.query.filter_by(body=querystring, engine_id=engine_id).first()
        result = None
        if query and query.segmentation is not None:
            result = query.segmentation
        elif query and query.segmentation is None:
            tokens = wam()
            result = ' | '.join(segment(querystring, engine_id, tokens))
            #Update Query table data
            q = Query.query.get(query.id)
            q.segmentation = result
            db.session.add(q)
            db.session.commit()
        else:
            tokens = wam()
            result = ' | '.join(segment(querystring, engine_id, tokens))
            #Insert data to Query table
            query = Query(body= querystring, segmentation = result, engine_id=engine_id, created_at=datetime.utcnow())
            db.session.add(query)
            db.session.commit()

        data = {'result': 'Success', 'text': result, 'message': ''}

        return json.dumps(data)
    return render_template('query.html')


@main.route('/upload', methods=['POST'])
def upload():
    if len(request.files) > 0:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename, filepath = save_file(file, UPLOAD_FILEPATH)

            engine_id = int(request.form.get('enginetype'))
            file = File(name=file.filename, path=filepath, status=0, engine_id=engine_id,\
                        deleted=0, created_at=datetime.utcnow())

            for row in read_file(filepath):
                query = Query.query.filter_by(body=row[0], engine_id=engine_id).first()
                if not query:
                    query = Query(body=row[0], engine_id=engine_id, created_at=datetime.utcnow())
                    db.session.add(query)
                file.queries.append(query)
            db.session.add(file)
            db.session.commit()
            flash({ 'status': 'success', 'text': 'Upload success.'})
            return redirect(url_for('.files'))
        else:
            flash({ 'status': 'failed', 'text': 'Please select the correct file type.'})
            return redirect(url_for('.files'))
    else:
        flash({ 'status': 'failed', 'text': 'Please select a file.'})
        return redirect(url_for('.files'))


@main.route('/files', methods=['GET','POST'])
def files():
    files = File.query.filter_by(deleted = 0).order_by(File.id.desc()).all()
    return render_template('files.html', files=files)


@main.route('/files/<int:file_id>')
def view_file(file_id = None):
    file = File.query.get(file_id)
    if file.deleted == 0:
        queries = file.queries.all()
        return render_template('view_file.html', queries=queries, file=file)
    else:
        return redirect(url_for('.files'))


@main.route('/files/download/<int:file_id>')
def download_file(file_id):
    filename = str(file_id) + '.xls'
    filepath = os.path.join(main.root_path, DOWNLOAD_FILEPATH, filename)
    file = File.query.get(file_id)
    temp_filename =None
    if file.engine_id == 2:
        temp_filename = 'Default AU 350 queries - ' + get_filename()  + '.xls'
    else:
        temp_filename = 'Default - ' + get_filename()  + '.xls'

    if not os.path.exists(filepath):
        file = File.query.get(file_id)
        queries = file.queries.all()
        write_excel_segmentation(queries, filepath)

    response = make_response(send_file(filepath))
    response.headers["Content-Disposition"] = "attachment;filename=%s;" % temp_filename
    return response


@main.route('/files/delete/<int:file_id>',methods = ['GET','POST'])
def delete_file(file_id):
    file = File.query.get(file_id)
    file.deleted = 1
    db.session.add(file)
    db.session.commit()
    flash({ 'status': 'success', 'text': 'Deleted success.'})
    return redirect(url_for('.files'))


@main.route('/comparison', methods = ['GET','POST'])
def comparison():
    comparisons = Comparison.query.filter_by(deleted = 0 ).order_by(Comparison.id.desc()).all()
    return render_template('comparison.html', comparisons = comparisons)


@main.route('/comparison_upload', methods = ['POST'])
def comparison_upload():
    if request.method == 'POST':
        comparisonName = request.form.get('comparisonNameInput')
        if comparisonName is None or comparisonName.strip() == '':
            flash({ 'status': 'failed', 'text': 'Please enter comparison name.'})
            return redirect(url_for('.comparison'))
        if len(request.files) == 2:
            auto_file = request.files['auto_file']
            manual_file = request.files['manual_file']

            if auto_file and allowed_file(auto_file.filename)  and manual_file and allowed_file(manual_file.filename):
                auto_new_filename, auto_filepath = save_file(auto_file, UPLOAD_COMPARISON_FILEPATH)
                manual_new_filename, manual_filepath = save_file(manual_file, UPLOAD_COMPARISON_FILEPATH)

                print auto_filepath
                print manual_filepath
                auto_file_data = read_file(auto_filepath)
                manual_file_data = read_file(manual_filepath)

                if len(auto_file_data) >0 and len(manual_file_data) > 0:
                    data = compare_data (auto_file_data,manual_file_data)
                    body = json.dumps(data)

                    item = Comparison(comparison_name = comparisonName,analysis_filename =auto_file.filename, analysis_filepath =auto_filepath, \
                            manual_filename  = manual_file.filename, manual_filepath = manual_filepath, body = body, \
                            partial_score = data['partial_score'], full_score = data['full_score'], total = data['total'],
                            score = data['score'], deleted  = 0, created_at=datetime.utcnow())
                    db.session.add(item)
                    db.session.commit()
                flash({ 'status': 'success', 'text': 'Upload success.'})
            else:
                flash({ 'status': 'failed', 'text': 'Please select the correct file type.'})
        else:
            flash({ 'status': 'failed', 'text': 'Please select two files to compare.'})
        return redirect(url_for('.comparison'))


@main.route('/delcomparison/<int:report_id>',methods =['GET','POST'])
def delcomparison(report_id):
    #comparison_data = Comparison.query.filter_by(id=report_id).first()
    comparison_data = Comparison.query.get(report_id)
    comparison_data.deleted = 1
    db.session.add(comparison_data)
    db.session.commit()
    flash({ 'status': 'success', 'text': 'Deleted success.'})
    return redirect(url_for('.comparison'))


@main.route('/report/<int:report_id>', methods = ['GET','POST'])
def report(report_id):
    comparison_data = Comparison.query.filter_by(id=report_id,deleted = 0).first()
    if comparison_data is None:
        return render_template('report.html', data = [], comparison = None)
    else:
        json_data = json.loads(comparison_data.body)
        return render_template('report.html', data = json_data['data'], comparison = comparison_data)


@main.route('/phraselist', methods = ['GET','POST'])
def phraselist():
    marklogics = Marklogic.query.filter_by(deleted = 0).order_by(Marklogic.id.desc()).all()
    return render_template('phraselist.html', items=marklogics)


@main.route('/phraselist/crud', methods = ['GET','POST'])
def phraselist_crud():
    if len(request.files) > 0:
        file = request.files['file']
        if file and allowed_file(file.filename):
            name = request.form.get('nameInput')
            epoch = request.form.get('epochNameInput')
            phraselist_name = request.form.get('phraseListNameInput')
            #refer_to = request.form.get('referToInput')
            crud = int(request.form.get('crudType'))
            env = int(request.form.get('envType'))
            if name is None or name.strip() == '' or epoch is None or epoch.strip() == '' or phraselist_name is None or phraselist_name.strip() == '' :
                flash({ 'status': 'failed', 'text': 'Please fill in all field.'})
                return redirect(url_for('.phraselist'))
            
            filename, filepath = save_file(file, UPLOAD_MARKLOGIC_FILEPATH)

            marklogic = Marklogic(name=name, filename = file.filename, filepath=filepath, \
                        epoch = epoch, phraselist_name =phraselist_name, \
                        env = env, status=0, crud= crud, deleted=0, created_at=datetime.utcnow())
                        
            db.session.add(marklogic)
            db.session.commit()
            flash({ 'status': 'success', 'text': 'Upload success.'})
            return redirect(url_for('.phraselist'))
        else:
            flash({ 'status': 'failed', 'text': 'Please select the correct file type.'})
            return redirect(url_for('.phraselist'))
    else:
        flash({ 'status': 'failed', 'text': 'Please select a file.'})
        return redirect(url_for('.phraselist'))


@main.route('/queryplan', methods =['GET','POST'])
def queryplan():
    marklogics = Marklogic.query.filter_by(deleted = 0, status = 2).order_by(Marklogic.id.desc()).all()
    phraselistnames = [ item.phraselist_name for item in marklogics]
    phraselistnames = list(set(phraselistnames))

    history = QueryPlans.query.filter_by(deleted = 0).order_by(QueryPlans.id.desc()).all()
    return render_template('queryplan.html', items = history, phraselistnames = phraselistnames)


@main.route('/queryplan_crud', methods = ['GET','POST'])
def queryplan_crud():
    if request.method == 'POST':
        name = request.form.get('nameInput')
        hlct = request.form.get('hlctType')
        phraselist_name = request.form.get('phraselistname')
        crud = int(request.form.get('crudType'))
        env = int(request.form.get('envType'))

        if name is None or name.strip() == '' :
            flash({ 'status': 'failed', 'text': 'Please enter QueryPlan name.'})
            return redirect(url_for('.queryplan'))

        queryplan = QueryPlans(queryplan_name = name, phraselist_name = phraselist_name, hlct_name = hlct, env = env, \
                               status=0, crud= crud, deleted=0, created_at=datetime.utcnow())
        db.session.add(queryplan)
        db.session.commit()

        try:
            handler = MarkLogicDataHandler(env, 'queryplan')
            headers = handler.get_headers()
            url = handler.get_url()
            body = handler.get_insert_queryplan_request_body(name)
            template = handler.get_insert_queryplan_template(hlct, phraselist_name)
            r = MarkLogicRequest(headers, url, body, template)
            r.post_insert_queryplan()
        except:
            flash({ 'status': 'failed', 'text': 'Add QueryPlan failed.'})
            queryplan.status = 2
        else:
            flash({ 'status': 'success', 'text': 'Add QueryPlan success.'})
            queryplan.status = 1
        finally:
            db.session.add(queryplan)
            db.session.commit()

    return redirect(url_for('.queryplan'))


@main.route('/queryset', methods = ['GET','POST'])
def queryset():
    if request.method == 'POST':
        if len(request.files) > 0:
            file = request.files['file']
            if file and allowed_file(file.filename):
                querySetName = request.form.get('querySetName')

                if querySetName is None and querySetName =='' :
                    flash({ 'status': 'failed', 'text': 'Please enter a QuerySetName.'})
                    return redirect(url_for('.queryset'))

                filename, filepath = save_file(file, UPLOAD_FILEPATH)
                data = [] 
                dic = { '1': ['guid', 'queryGuid'], '2': ['term', 'expr']}

                for row in read_file(filepath):
                    name = row[2]
                    if name and name is not None and name !='' and name.strip().lower() == querySetName.strip().lower():                        
                        data.append( { 'guid': row[5], 'term' : row[6]})

                filename = 'Template.xls'
                filepath = os.path.join(main.root_path, DOWNLOAD_FILEPATH, filename)
                print data
                write_excel(data, dic, filepath)
                response = make_response(send_file(filepath))
                response.headers["Content-Disposition"] = "attachment;filename=%s;" % filename
                return response
        else:
            flash({ 'status': 'failed', 'text': 'Please select a file.'})
            return redirect(url_for('.queryset'))
    else:
        return render_template('queryset.html')



def compare_data(auto_file_data, manual_file_data):
    array = []
    not_match = []
    index = 1
    total = 0
    count = 0
    partial_score = 0
    full_score = 0

    for row in auto_file_data:
        segmentation = get_segmentation_data(manual_file_data, row)
        if segmentation != None:
            item = {'id': index,'query': row[0],'auto_segmentation': row[1],'manual_segmentation': segmentation[0],'score': segmentation[1]}
            if segmentation[1] == 1.0 :
                count = count + 1
                full_score = full_score + 1
            partial_score = partial_score + segmentation[1]
            total = total + 1
            array.append(item)
        else:
            not_match.append(row)
        index = index + 1
    score = round(float(count) / float(total), 2)
    return {'data': array,'not_match': not_match,'score': score, 'partial_score': partial_score, 'full_score':full_score, 'total': total}


def get_segmentation_data(data, query):
    result = None
    for item in data:
        if item[0].lower() == query[0].lower():
            score = compare_segmentation(query[1], item[1])
            return item[1], score


def normalize_segmentation(str):
    """1. AB => ab
       2. [a b] => [a] | [b]
       3. "ab" => ab
       4. [a] => a
       5. a|b => a | b
       5. '   ' => ' '"""
    str = str.strip().lower()
    str = re.sub(r'\[([a-z0-9]+ [a-z0-9 ]+)\]', lambda x: '[' + '] | ['.join(x.group(1).split(' ')) + ']', str)
    str = re.sub(r'"([^"]+)"', "\g<1>", str)
    str = re.sub(r'\[([^\]]+)\]', "\g<1>", str)
    str = str.replace('|', ' | ')
    str = re.sub(r' +', ' ', str)
    return str


def compare_segmentation(segmentation, expected_segmentation):
    segmentation = normalize_segmentation(segmentation)
    expected_segmentation = normalize_segmentation(expected_segmentation)
    print segmentation
    print expected_segmentation

    if segmentation == expected_segmentation:
        return 1.0
    else:
        terms = segmentation.split(' | ')
        expected_terms = expected_segmentation.split(' | ')
        intersection = [x for x in terms if x in expected_terms]
        return round(len(intersection) * 1.0 / len(terms), 2)
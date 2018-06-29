from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, make_response, send_file, flash
from . import main
from .forms import NameForm
from .. import db
from ..models import Survey, SurveyScore
from .common import allowed_file, get_file_extension, wam, segment, get_filename, read_file, write_excel_segmentation, write_excel, save_file
import json
import os
import re
import time
import uuid
import base64
from .marklogic import MarkLogicDataHandler, MarkLogicRequest
from sqlalchemy import and_
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads/json'
ALLOWED_EXTENSIONS = set(['json'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@main.route('/')
def index():
    array = []
    datasets = Survey.query.filter_by(
        type_code=0).order_by(Survey.id.asc()).all()
    for item in datasets:
        setattr(item, 'survey', json.loads(item.json_content))
        array.append(item)
    return render_template('index.html', dataSetList=array)


@main.route('/surveylist/<string:parent_id>', methods=['GET'])
def surveylist(parent_id):
    array = []
    # surveys = Survey.query.outerjoin(SurveyScore,Survey.id == SurveyScore.survey_id).filter(
    #     Survey.type_code==1, Survey.parent_pkey==parent_id).order_by(Survey.id.asc()).all()
    surveys = db.session.query(Survey, SurveyScore).outerjoin(SurveyScore, and_(
        Survey.id == SurveyScore.survey_id)).filter(Survey.parent_pkey == parent_id, Survey.type_code == 1).all()

    for item in surveys:
        array.append({'survey': json.loads(item[0].json_content),
                      'id': item[0].id,
                      'status': (0 if item[1] == None else item[1].status)})

    return render_template('surveylist.html', surveyList=array)


@main.route('/survey/<int:svy_id>', methods=['GET'])
def survey(svy_id):
    survey = Survey.query.get(svy_id)
    dataset = Survey.query.filter_by(
        type_code=0, pkey=survey.parent_pkey).first()
    svy_score = SurveyScore.query.filter_by(
        survey_id=svy_id).order_by(SurveyScore.id.desc()).first()

    info = json.loads(dataset.json_content)
    svy_content = json.loads(survey.json_content)

    obj = {}
    for item in svy_content['recommend']:
        obj[item['legislation']['jurisdiction']] = item['legislation']['jurisdiction']

    keys = obj.keys()

    for key in keys:
        arrTemp = []
        for item in svy_content['recommend']:
            if item['legislation']['jurisdiction'] == key :
                arrTemp.append(item)
        obj[key] = arrTemp[:]

    svy_content['jurisdictions'] = obj

    return render_template('survey.html', survey=svy_content, info=info['info'], svy_score=svy_score, svy_id=svy_id, parent_pkey=survey.parent_pkey)


@main.route('/surveyids/<string:parent_id>', methods=['GET'])
def surveyids(parent_id):
    array = []
    try:
        # surveys = Survey.query.filter_by(
        #     type_code=1, parent_pkey=parent_id).order_by(Survey.id.asc()).all()
        surveys = db.session.query(Survey, SurveyScore).outerjoin(
            SurveyScore, and_(Survey.id == SurveyScore.survey_id)).filter(Survey.parent_pkey == parent_id, Survey.type_code == 1).all()
        for item in surveys:
            array.append({'id': item[0].id, 'status': (
                0 if item[1] == None else item[1].status)})
        data = {'result': 'Success', 'ids': array}
    except Exception, e:
        data = {'result': 'Error', 'message': e.message}
    return json.dumps(data)


@main.route('/survey/completed/<int:svy_id>', methods=['POST'])
def survey_completed(svy_id):
    try:
        score = request.form.get('score')
        comments = request.form.get('comments')
        status = request.form.get('status')
        svy_score = SurveyScore.query.filter_by(
            survey_id=svy_id).order_by(SurveyScore.id.desc()).first()
        if svy_score == None:
            svy_score = SurveyScore(survey_id=svy_id, score=score, status=status,
                                    comments=comments, lastupdate_date=datetime.utcnow())
            db.session.add(svy_score)
        else:
            svy_score.score = score
            svy_score.comments = comments
            svy_score.status = status
            svy_score.lastupdate_date = datetime.utcnow()
        db.session.commit()
        db.session.close()
        data = {'result': 'Success'}
    except Exception, e:
        data = {'result': 'Error', 'message': e.message}
    return json.dumps(data)


@main.route('/survey/survey_completed_succ', methods=['GET'])
def survey_completed_succ():
    return render_template('survey_completed_succ.html')


def save_json(json_text):
    pkey = str(uuid.uuid4())
    
    dataset_svy = Survey(pkey=pkey, parent_pkey='0', json_content=json_text,
                            type_code=0, lastupdate_date=datetime.utcnow())
    db.session.add(dataset_svy)
    db.session.commit()

    dataset_content = json.loads(json_text)
    group = dataset_content['group']
    for item in group:
        query_svy = Survey(pkey=str(uuid.uuid4()), parent_pkey=pkey, json_content=json.dumps(
            item), type_code=1, lastupdate_date=datetime.utcnow())
        db.session.add(query_svy)
        db.session.commit()
    db.session.close()

@main.route('/upload_json', methods=['GET', 'POST'])
def upload_json():
    if request.method == 'GET':
        return render_template('upload_json.html')
    else:
        try:
            json_text = request.form.get('json_text')
            save_json(json_text)
            data = {'result': 'Success'}
        except Exception, e:
            data = {'result': 'Error', 'message': e.message}
        return json.dumps(data)


@main.route('/upload_file', methods=['GET', 'POST'], strict_slashes=False)
def upload_file():
    if request.method == 'GET':
        return render_template('upload_file.html')
    else:
        try:
            file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            f = request.files['file']
            if f and allowed_file(f.filename):
                fname = secure_filename(f.filename)
                print fname
                ext = fname.rsplit('.', 1)[1]
                unix_time = int(time.time())
                new_filename = str(unix_time)+'.'+ext
                f.save(os.path.join(file_dir, new_filename))
                token = base64.b64encode(new_filename)
                #print token
                data = {'result': 'Success', "token": token}
                json_content = open(os.path.join(file_dir, new_filename)).read()
                #print json_content
                save_json(json_content)
                return render_template('upload_file_succ.html', message='Thank you! The file "'+fname+'" has been upload successful')
            else:
                data = {'result': 'Error', "message": "File not allowed"}
                return render_template('upload_file_succ.html', message='Sorry,File not allowed! Only JSON file allowed to be upload!')
        except Exception, e:
            data = {'result': 'Error', 'message': e.message}
            return render_template('upload_file_succ.html', message=e.message)


@main.route('/dataset/delete/<string:pkey>', methods=['POST'])
def dataset_delete(pkey):
    try:
        surveys = db.session.query(Survey, SurveyScore).outerjoin(
            SurveyScore, and_(Survey.id == SurveyScore.survey_id)).filter(Survey.parent_pkey == pkey, Survey.type_code == 1).all()
        for item in surveys:
            db.session.delete(item[0])
            if item[1] != None:
                db.session.delete(item[1])
        Survey.query.filter_by(type_code=0, pkey=pkey).delete(
            synchronize_session=False)
        db.session.commit()
        db.session.close()
        data = {'result': 'Success'}
    except Exception, e:
        data = {'result': 'Error', 'message': e.message}
    return json.dumps(data)

from datetime import datetime
from flask import render_template, request, redirect, url_for, make_response, send_file, flash
from . import main
from .forms import NameForm
from .. import db
from ..models import Survey, SurveyScore
from .common import allowed_file, get_file_extension, wam, segment, get_filename, read_file, write_excel_segmentation, write_excel, save_file
import json
import os
import re
import uuid
from .marklogic import MarkLogicDataHandler, MarkLogicRequest
from sqlalchemy import and_

UPLOAD_FILEPATH = 'uploads'
DOWNLOAD_FILEPATH = 'downloads'
UPLOAD_COMPARISON_FILEPATH = 'uploads/comparisons'
UPLOAD_MARKLOGIC_FILEPATH = 'uploads/marklogics'

#DICTIONARY ={'[a]': 'a','[can]': 'can','[for]': 'for','[in]': 'in', '[by]':'by'}


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
                      'status':(0 if item[1]==None else item[1].status)})

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
            array.append({'id': item[0].id, 'status': (0 if item[1]==None else item[1].status)})
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

        data = {'result': 'Success'}
    except Exception, e:
        data = {'result': 'Error', 'message': e.message}
    return json.dumps(data)


@main.route('/survey/survey_completed_succ', methods=['GET'])
def survey_completed_succ():
    return render_template('survey_completed_succ.html')


@main.route('/upload_json', methods=['GET', 'POST'])
def upload_json():
    if request.method == 'GET':
        return render_template('upload_json.html')
    else:
        try:
            pkey = str(uuid.uuid4())
            json_text = request.form.get('json_text')
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

            data = {'result': 'Success'}
        except Exception, e:
            data = {'result': 'Error', 'message': e.message}
        return json.dumps(data)

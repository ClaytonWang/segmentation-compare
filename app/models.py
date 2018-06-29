from . import db
from sqlalchemy.dialects import mysql

class Survey(db.Model):
    __tablename__ = 'surveys'
    id = db.Column(db.Integer,primary_key=True)
    pkey = db.Column(db.String(100))
    parent_pkey = db.Column(db.String(100))
    json_content = db.Column(mysql.LONGTEXT )
    type_code =  db.Column(db.Integer) #0 -- data set; 1 -- query
    lastupdate_date = db.Column(db.DateTime)
    


class SurveyScore(db.Model):
    __tablename__ = 'surveyscores'
    id = db.Column(db.Integer,primary_key=True)
    survey_id  = db.Column(db.Integer)
    score = db.Column(db.String(1000))
    status = db.Column(db.Integer, default = 0)
    comments = db.Column(db.TEXT)
    lastupdate_date = db.Column(db.DateTime)

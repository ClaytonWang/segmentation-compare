from . import db

class Survey(db.Model):
    __tablename__ = 'surveys'
    id = db.Column(db.Integer,primary_key=True)
    pkey = db.Column(db.String(100))
    parent_pkey = db.Column(db.String(100))
    json_content = db.Column(db.Text)
    type_code =  db.Column(db.Integer) #0 -- data set; 1 -- query
    lastupdate_date = db.Column(db.DateTime)
    


class SurveyScore(db.Model):
    __tablename__ = 'surveyscores'
    id = db.Column(db.Integer,primary_key=True)
    survey_id  = db.Column(db.Integer)
    score = db.Column(db.String(10))
    status = db.Column(db.Integer, default = 0)
    comments = db.Column(db.Text)
    lastupdate_date = db.Column(db.DateTime)

from . import db

files_queries = db.Table('files_queries',
    db.Column('file_id', db.Integer, db.ForeignKey('files.id')),
    db.Column('query_id', db.Integer, db.ForeignKey('queries.id'))
)

class Survey(db.Model):
    __tablename__ = 'surveys'
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.String)
    comments = db.Column(db.String)
    score = db.Column(db.String)
    status = db.Column(db.Integer)
    # algorisms = db.Column(db.String)
    # datasetName = db.Column(db.String)
    # seconds = db.Column(db.Integer)
    # date = db.Column(db.DateTime)
    lastupdate_date = db.Column(db.DateTime)

class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    path = db.Column(db.String)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    engine_id = db.Column(db.SmallInteger)
    status = db.Column(db.SmallInteger)
    deleted = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime)
    queries = db.relationship('Query', secondary=files_queries,
                                    backref=db.backref('files', lazy='dynamic'),
                                    lazy='dynamic')


class Query(db.Model):
    __tablename__ = 'queries'
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String)
    segmentation = db.Column(db.String)
    engine_id = db.Column(db.SmallInteger)
    created_at = db.Column(db.DateTime)


class Comparison(db.Model):
    __tablename__ = 'comparisons'
    id = db.Column(db.Integer, primary_key = True)
    comparison_name = db.Column(db.String)
    analysis_filename = db.Column(db.String)
    analysis_filepath = db.Column(db.String)
    manual_filename = db.Column(db.String)
    manual_filepath = db.Column(db.String)
    body = db.Column(db.String)
    score = db.Column(db.String)
    full_score = db.Column(db.String)
    partial_score = db.Column(db.String)
    total = db.Column(db.SmallInteger)
    deleted = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime)


class Marklogic(db.Model):
    __tablename__ = 'marklogics'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    filename = db.Column(db.String)
    filepath = db.Column(db.String)
    referto = db.Column(db.String)
    epoch = db.Column(db.String)
    phraselist_name = db.Column(db.String)
    failed = db.Column(db.SmallInteger)
    success = db.Column(db.SmallInteger)
    total = db.Column(db.SmallInteger)
    status = db.Column(db.SmallInteger)
    crud = db.Column(db.SmallInteger)
    env = db.Column(db.SmallInteger)
    deleted = db.Column(db.Boolean)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime)


class QueryPlans(db.Model):
    __tablename__ = 'queryplans'
    id = db.Column(db.Integer, primary_key = True)
    queryplan_name = db.Column(db.String)
    phraselist_name = db.Column(db.String)
    hlct_name = db.Column(db.String)
    referto = db.Column(db.String)
    status = db.Column(db.SmallInteger)
    crud = db.Column(db.SmallInteger)
    env = db.Column(db.SmallInteger)
    deleted = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime)
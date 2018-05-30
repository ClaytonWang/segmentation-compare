#!/usr/bin/env python
import os
from app import create_app, db
from app.main.common import wam, segment, read_file
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from datetime import datetime
import sys
import time
from app.main.marklogic import MarkLogicDataHandler, MarkLogicRequest

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


# @manager.command
# def test():
#     """Run the unit tests."""
#     import unittest
#     tests = unittest.TestLoader().discover('tests')
#     unittest.TextTestRunner(verbosity=2).run(tests)


# @manager.command
# def worker():
#     while True:
#         file = File.query.filter_by(status=0).limit(1).first()
#         if not file:
#             time.sleep(10)
#             continue
#         file.start_time = datetime.utcnow()
#         file.status = 1
#         db.session.add(file)
#         db.session.commit()
#         tokens = wam()
#         for query in file.queries.all():
#             print(query.segmentation)
#             if query.segmentation is None:
#                 segmentation = ' | '.join(segment(query.body, query.engine_id, tokens))
#                 q = Query.query.get(query.id)
#                 q.segmentation = segmentation
#                 db.session.add(q)
#                 db.session.commit()
#                 print query.id, query.body, segmentation
#         file.end_time = datetime.utcnow()
#         file.status = 2
#         db.session.add(file)
#         db.session.commit()


# @manager.command
# def marklogic_worker():
#     while True:
#         marklogic = Marklogic.query.filter_by(status=0).limit(1).first()
#         if not marklogic:
#             print "Don't have the data."
#             time.sleep(10)
#             continue
#         print "Start Run"

#         marklogic.start_time = datetime.utcnow()
#         marklogic.status = 1
#         db.session.add(marklogic)
#         db.session.commit()
        
#         try:
#             handler = MarkLogicDataHandler(marklogic.env,'phraselist')
#             headers = handler.get_headers()
#             url = handler.get_url()
#             body = handler.get_insert_phrase_request_body()
#             template = handler.get_insert_phrase_template(marklogic.epoch, marklogic.phraselist_name)
#             #count_body = handler.get_count_request_body(marklogic.epoch)
#             request = MarkLogicRequest(headers, url, body, template)

#             phrases = read_file(marklogic.filepath)
#             count = 0
#             success = 0
#             if marklogic.crud == 1:
#                 for row in phrases:
#                     phrase = row[0]
#                     print(phrase)
#                     success += request.post_insert_phrase(phrase)
#                     count += 1
#             else:
#                 for row in phrases:
#                     phrase = row[0]
#                     print(phrase)
#                     success += request.post_delete(phrase)
#                     count += 1

#             #count = request.post_result(count_body)  
#             marklogic.total = count
#             marklogic.success = success
#             marklogic.end_time = datetime.utcnow()

#             print marklogic.end_time - marklogic.start_time

#         except Exception as e:
#             print e
#             marklogic.status = 3
#         else:
#             marklogic.status = 2
#         finally:
#             db.session.add(marklogic)
#             db.session.commit()

#         print "End Run"

if __name__ == '__main__':
    manager.run()

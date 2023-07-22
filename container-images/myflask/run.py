from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time
import traceback
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://{}:{}$@pgpool.postgresql:5432/testdb'.format(os.environ['user'],os.environ['password'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class TestTable(db.Model):
  __tablename__ = 'test_table'
  id = db.Column(db.Integer, primary_key=True)
  num = db.Column(db.Integer)
  data = db.Column(db.Text)

@app.before_first_request
def init():
  db.create_all()

@app.route('/')
def hello_world():
  try:
    now = datetime.now()
    tt=TestTable(num=1, data=now.strftime("%Y-%m-%d %H:%M:%S.%f"))
    db.session.add(tt)
    db.session.commit()

  except Exception as e:
    db.session.rollback()
    print("****  DB Error  ****")
    print(traceback.format_exc())

  return 'OK'

if __name__ == '__main__':
  app.run()

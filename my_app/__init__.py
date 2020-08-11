from flask import Flask, request, render_template, jsonify, Blueprint, flash, redirect, url_for
import json
from my_app.tasks import task as t
import my_app.worker as w
from datetime import datetime, timedelta

from celery_sqlalchemy_scheduler.session import SessionManager
from my_app.celeryconfig import beat_dburi,login_dburi
from celery_sqlalchemy_scheduler.models import PeriodicTask, CrontabSchedule, IntervalSchedule
import pytz

from flask_login import LoginManager, login_required
from flask_sqlalchemy import SQLAlchemy

session_manager = SessionManager()
engine, Session = session_manager.create_session(beat_dburi)
session = Session()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = login_dburi
app.config['WTF_CSRF_SECRET_KEY'] = 'asdijhasdkjh21e72uqwhi(65)'
db = SQLAlchemy(app)

app.secret_key = 'asda12179yweiuhsfdeasdfkjh'
 
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.init_app(app)
login_manager.login_view = 'login'
 
from my_app.auth.views import auth
app.register_blueprint(auth)

db.create_all()

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

@app.route('/obiextract', methods=['GET','POST'])
@login_required
def obiextract():
    if request.method == 'GET':
        return render_template('obiextract.html')    

    if request.method == 'POST':
         cronSchedule = (request.form['cron']).split()         
         jobname = request.form['jobname']
         schedule = createSchedule(cronSchedule)
         args=[]

         args.append('--reportpath=' + request.form['reportpath'])
         args.append('--frcenv=' + request.form['frcenv'])
         args.append('--racfid=' + request.form['racfid'])
         args.append('--department=' + request.form['department'])

         if request.form['target'] == 'Tableau':
           args.append('Tableau')
           args.append('--project=' + request.form['project'])
           args.append('--filename=' + request.form['filename'])
           args.append('--tabenv=' + request.form['tabenv'])
           args.append('--mode=' + request.form['tabmode'])
         else:
           args.append('Database')
           args.append('--tablename=' + request.form['tablename'])
           args.append('--mode=' + request.form['dbmode'])
           args.append('--database=' + request.form['database'])

         createPeriodicTask(jobname, 'my_app.tasks.task.obiextract', args, schedule)
         flash(jobname + ' scheduled successfully', 'success')

         return redirect(url_for('auth.home'))         

@app.route('/unpivot', methods=['GET','POST'])
@login_required
def unpivot():
    if request.method == 'GET':
        return render_template('unpivot.html')    

    if request.method == 'POST':
         jobname = request.form['jobname']
         filename = request.form['filename']
         sheet = request.form['sheet']
         database = request.form['database']
         mode = request.form['mode']
         tablename = request.form['tablename']
         args = [filename,sheet,database,mode,tablename]
         cronSchedule = (request.form['cron']).split()         
         schedule = createSchedule(cronSchedule)
         createPeriodicTask(jobname, 'my_app.tasks.task.unpivot', args, schedule)
         
         flash(jobname + ' scheduled successfully', 'success')
         return redirect(url_for('auth.home'))         


def createSchedule(cronSchedule):
    schedule = CrontabSchedule(
        minute=cronSchedule[0],  
        hour=cronSchedule[1],
        day_of_week=cronSchedule[2],
        day_of_month=cronSchedule[3],
        month_of_year=cronSchedule[4],
        timezone='Europe/London'         
    )
    session.add(schedule)
    session.commit()
    return schedule
         
def createPeriodicTask(jobname, taskname, arguements,schedule):
    periodic_task = PeriodicTask(
      crontab=schedule,
      name=jobname,
      task=taskname,
      args=json.dumps(arguements)
    )
    session.add(periodic_task)
    session.commit()


if __name__ == '__main__':
    app.run(debug=True, port=5000)

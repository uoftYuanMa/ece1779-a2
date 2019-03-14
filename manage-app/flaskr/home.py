from flask import render_template, url_for, session, redirect, request
from flaskr import app
from flaskr.aws import aws
import traceback
import json

awscli = aws.AwsClient()

@app.route('/')
@app.route('/home')
def home():
    user = session['user'] if 'user' in session else None
    if not user:
        return redirect(url_for('login'))
    else:
        try:
            return render_template('home.html')
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            return render_template('error.html', msg='something goes wrong~')

@app.route('/fetch_workers')
def fetch_workers():
    target_instances = awscli.get_target_instances()
    ret = {'data': target_instances}
    return json.dumps(ret)


@app.route('/fetch_cpu_utils', methods=['GET', 'POST'])
def fetch_cpu_utils():
    instances = json.loads(request.data.decode('utf-8'))
    series = []
    for instance in instances:
        series.append({
            "name": instance,
            "data": awscli.get_cpu_utils(instance)
        })
    return json.dumps(series)

@app.route('/fetch_requests_rate', methods=['GET', 'POST'])
def fetch_reqeusts_rate():
    instances = json.loads(request.data.decode('utf-8'))
    series = []
    for instance in instances:
        series.append({
            "name": instance,
            "data": awscli.get_requests_per_minute(instance)
        })
    return json.dumps(series)

@app.route('/grow_one_worker', methods=['GET', 'POST'])
def grow_one_worker():
    if awscli.get_idle_instances():
        awscli.grow_worker_by_one()
        flag = True
        msg = 'success'
    else:
        flag = False
        msg = 'no idle instances'

    return json.dumps({
        'flag': flag,
        'msg': msg
    })

@app.route('/shrink_one_worker', methods=['GET', 'POST'])
def shrink_one_worker():
    if awscli.get_target_instances():
        awscli.shrink_work_by_one()
        flag = True
        msg = 'success'
    else:
        flag = False
        msg = 'No workers in pool'

    return json.dumps({
        'flag': flag,
        'msg': msg
    })

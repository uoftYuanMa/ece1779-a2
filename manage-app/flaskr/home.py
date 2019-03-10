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
    """
    :return:
    """
    # awscli.grow_worker_by_one()
    # return redirect(url_for('home'))

@app.route('/add_one_worker', methods=['GET', 'POST'])
def shrink_one_worker():
    """
    :return:
    """
    # awscli.shrink_worker_by_one()
    # return redirect(url_for('home'))
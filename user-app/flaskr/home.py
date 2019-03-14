from flask import render_template, url_for, session, redirect
from flaskr import app
from flaskr import db
from datetime import datetime
from flaskr.models import Image
from flaskr.models import RequestPerMinute
from sqlalchemy import desc
import traceback

def get_faces(img):
    name, type = img.rsplit('.')
    return name + '_faces.' + type

def get_thumbs(img):
    name, type = img.rsplit('.')
    return name + '_thumb.' + type

@app.route('/')
@app.route('/home')
def home():
    user = session['user'] if 'user' in session else None
    if not user:
        return redirect(url_for('login'))
    else:
        try:
            images = Image.query.filter_by(userid=user['userid'])
            images = [[image.imageid, get_thumbs(image.path), image.path,
                       get_thumbs(get_faces(image.path)), get_faces(image.path)] for image in images]
            return render_template('home.html', images=images)
        except Exception as e:
            # print(e)
            traceback.print_tb(e.__traceback__)
            return render_template('error.html', msg='something goes wrong~')


def record_requests(instance_id):
    requests = RequestPerMinute(instance_id=instance_id, timestamp=datetime.now())
    db.session.add(requests)
    db.session.commit()
    return print(RequestPerMinute.query.order_by(desc(RequestPerMinute.timestamp)).first())

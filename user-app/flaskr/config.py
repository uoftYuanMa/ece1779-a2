import os
basedir = os.path.abspath(os.path.dirname(__file__))

def get_instanceId():
    return os.popen('ec2metadata --instance-id').read().strip()

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ece1779-a2-secretkey'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'mysql+pymysql://ece1779liuwl:ece1779liuwl@ece1779-db.cwufnxxah8dq.us-east-1.rds.amazonaws.com/ece1779'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = basedir + '/static/images'
    ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']
    BUCKET_NAME = 'ece1779-images'
    INSTANCE_ID = get_instanceId()
    ZONE = 'Canada/Eastern'

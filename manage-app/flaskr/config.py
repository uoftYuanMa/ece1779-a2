import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ece1779-a2-secretkey'
    BUCKET_NAME = 'ece1779-images'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'mysql+pymysql://ece1779liuwl:ece1779liuwl@ece1779-db.cwufnxxah8dq.us-east-1.rds.amazonaws.com/ece1779'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ZONE = 'Canada/Eastern'

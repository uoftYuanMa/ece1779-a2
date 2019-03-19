from flaskr import db
from flaskr import app
from flaskr.models import RequestPerMinute
from pytz import timezone
from datetime import datetime

def record_requests(instance_id):
    try:
        requests = RequestPerMinute(instance_id=instance_id,
                                    timestamp=datetime.now(timezone(app.config['ZONE'])))
        db.session.add(requests)
        db.session.commit()
    except Exception as e:
        print(e)

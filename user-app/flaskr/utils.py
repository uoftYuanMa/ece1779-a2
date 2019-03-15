from flaskr import db
from datetime import datetime
from flaskr.models import RequestPerMinute
from sqlalchemy import desc


def record_requests(instance_id):
    try:
        requests = RequestPerMinute(instance_id=instance_id, timestamp=datetime.now())
        db.session.add(requests)
        db.session.commit()
    except Exception as e:
        print(e)

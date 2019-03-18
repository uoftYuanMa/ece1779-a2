import sys
sys.path.append('../../')
import schedule
import time
from datetime import datetime, timedelta
from pytz import timezone
from flaskr import app
from flaskr import db
from flaskr.models import AutoScalingConfig, RequestPerMinute
from sqlalchemy import desc
import aws

awscli = aws.AwsClient()

# get start_time and end_time of latest 1 minute
def get_one_minute_time_span(latest):
    end_time = datetime.now(timezone(app.config['ZONE']))
    start_time = end_time - timedelta(seconds=latest)
    return start_time, end_time

def current_config():
    return AutoScalingConfig.query.order_by(desc(AutoScalingConfig.timestamp)).first()

def average_request_rate():
    valid_instances_num = len(awscli.get_valid_target_instances())
    start_time, end_time = get_one_minute_time_span(60)
    datetimes = RequestPerMinute.query.filter(RequestPerMinute.timestamp >= start_time) \
        .filter(RequestPerMinute.timestamp <= end_time) \
        .with_entities(RequestPerMinute.timestamp).all()
    return len(datetimes) / valid_instances_num if valid_instances_num else -1


def auto_scaling():
    current_time = datetime.now()
    request_rate = average_request_rate()

    # if there is no valid instances, then do nothing.
    if request_rate == -1:
        print('{} no workers in the pool'.format(current_time))
        return

    response = ''
    config = current_config()
    #cpu_grow, cpu_shrink, ratio_expand, ratio_shrink
    if request_rate > config.cpu_grow:
        response = awscli.grow_worker_by_ratio(config.ratio_expand)
        print('{} grow workers: {}'.format(current_time, response))
    elif request_rate < config.cpu_shrink:
        response = awscli.shrink_worker_by_ratio(config.ratio_shrink)
        print('{} shrink workers: {}'.format(current_time, response))
    else:
        print('{} nothing change'.format(current_time))


def clear_requests():
    # clear the records 2 hours ago
    start_time, end_time = get_one_minute_time_span(7200)
    RequestPerMinute.query.filter(RequestPerMinute.timestamp < start_time).delete()
    db.session.commit()
    print('{} delete records two hours go'.format(end_time))


if __name__ == '__main__':
    # start auto-scaling
    schedule.every().minute.do(auto_scaling)
    schedule.every().minute.do(clear_requests)
    while True:
        schedule.run_pending()
        time.sleep(1)

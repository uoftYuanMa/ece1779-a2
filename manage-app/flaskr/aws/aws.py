import boto3
import json
from datetime import datetime, timedelta

class AwsClient:
    def __init__(self):
        self.elb = boto3.client('elbv2')
        self.TargetGroupArn = 'arn:aws:elasticloadbalancing:us-east-1:536627286469:targetgroup/target-group1/c0b38de79630ee69'
        self.cloudwatch = boto3.client('cloudwatch')

    def get_workers(self):
        response = self.elb.describe_target_health(
            TargetGroupArn=self.TargetGroupArn,
        )
        if 'TargetHealthDescriptions' in response:
            instances = []
            for target in response['TargetHealthDescriptions']:
                instances.append({
                    'Id': target['Target']['Id'],
                    'Port': target['Target']['Port'],
                    'State': target['TargetHealth']['State']
                })
            ret = {'data': instances}
            return json.dumps(ret)
        else:
            return []

    def get_cpu_utils(self, instance_id):
        end_time = datetime.now() - timedelta(seconds=60)
        start_time = end_time - timedelta(seconds=3600)
        response = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance_id
                },
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=[
                'Maximum',
            ],
            Unit='Percent'
        )
        if 'Datapoints' in response:
            datapoints = []
            for datapoint in response['Datapoints']:
                datapoints.append([
                    int(datapoint['Timestamp'].timestamp()*1000),
                    float(datapoint['Maximum'])
                ])
            return json.dumps(sorted(datapoints, key=lambda x:x[0]))
        else:
            return []

    def get_requests_per_minute(self, instance_id):
        """
        :param instance_id: str
        :return: list of [timestamp:int, requests rate:float]
        """
        end_time = datetime.now() - timedelta(seconds=60)
        start_time = end_time - timedelta(seconds=3660)
        response = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='NetworkPacketsIn',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance_id
                },
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=[
                'Average',
            ],
            Unit='Count'
        )

        if 'Datapoints' in response:
            datapoints = []
            for datapoint in response['Datapoints']:
                datapoints.append([
                    int(datapoint['Timestamp'].timestamp() * 1000),
                    float(datapoint['Average'])
                ])
            return json.dumps(sorted(datapoints, key=lambda x: x[0]))
        else:
            return []

    def get_idle_instances(self):
        """
        return idle instances
        :return: instances: list
        """
        pass

    def grow_worker_by_one(self):
        """
        add one instance into the self.TargetGroupArn
        :return: msg: str
        """
        pass

    def grow_worker_by_ratio(self, ratio):
        """
        add one instance into the self.TargetGroupArn
        :return: msg: str
        """
        pass

    def shrink_work_by_one(self):
        """
        shrink one instance into the self.TargetGroupArn
        :return: msg: str
        """
        pass

    def shrink_work_by_ratio(self, ratio):
        """
        shrink one instance into the self.TargetGroupArn
        :return: msg: str
        """
        pass

if __name__ == '__main__':
    awscli = AwsClient()
    #print(awscli.get_workers())
    print(awscli.get_requests_per_minute('i-010c40a69aa1bcbd7'))

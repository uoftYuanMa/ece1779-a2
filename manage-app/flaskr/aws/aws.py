import boto3
import json
from datetime import datetime, timedelta

class AwsClient:
    def __init__(self):
        self.ec2 = boto3.client('ec2')
        self.elb = boto3.client('elbv2')
        self.TargetGroupArn = 'arn:aws:elasticloadbalancing:us-east-1:536627286469:targetgroup/target-group1/c0b38de79630ee69'
        self.cloudwatch = boto3.client('cloudwatch')
        self.user_app_tag = 'user-app-ece1779-a2'

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
                for i in range(60//len(response['Datapoints'])):
                    datapoints.append([
                        int(datapoint['Timestamp'].timestamp()*1000),
                        float(datapoint['Average'])
                    ])
                
            return json.dumps(sorted(datapoints, key=lambda x:x[0]))
        else:
            return []

        pass

    def get_tag_instances(self):
        instances = []
        custom_filter = [{
            'Name': 'tag:Name',
            'Values': [self.user_app_tag]}]
        response = self.ec2.describe_instances(Filters=custom_filter)
        #instance_id = response['Reservations'][0]['Instances'][0]['InstanceId']
        reservations = response['Reservations']
        for reservation in reservations:
            if len(reservation['Instances']) > 0:
                instances.append({
                 'Id': reservation['Instances'][0]['InstanceId']
                })
        return instances

    def get_target_instances(self):
        response = self.elb.describe_target_health(
            TargetGroupArn=self.TargetGroupArn,
        )
        instances = []
        if 'TargetHealthDescriptions' in response:
            for target in response['TargetHealthDescriptions']:
                instances.append({
                    'Id': target['Target']['Id'],
                    'Port': target['Target']['Port'],
                    'State': target['TargetHealth']['State']
                })
        return instances

    def get_idle_instances(self):
        """
        return idle instances
        :return: instances: list
        """
        instances_tag_raw = self.get_tag_instances()
        instances_target_raw = self.get_target_instances()
        instances_tag =[]
        instances_target = []
        for item in instances_tag_raw:
            instances_tag.append(item['Id'])
        for item in instances_target_raw:
            instances_target.append(item['Id'])
        diff_list = []
        for item in instances_tag:
            if item not in instances_target:
                diff_list.append(item)
        
        return diff_list

    def grow_worker_by_one(self):
        """
        add one instance into the self.TargetGroupArn
        :return: msg: str
        register_targets(**kwargs)
        """
        idle_instances = self.get_idle_instances()
        if idle_instances:
            first_idle_instance = idle_instances[0]
            response = self.elb.register_targets(
                TargetGroupArn = self.TargetGroupArn,
                Targets=[
                    {
                        'Id': first_idle_instance,
                        'Port': 5000
                    },
                ]
            )
            if response and 'ResponseMetadata' in response and \
                    'HTTPStatusCode' in response['ResponseMetadata']:
                return response['ResponseMetadata']['HTTPStatusCode']
            else:
                return 'Fail to register new worker'
        else:
            return 'No more idle instances'

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
        valid = '500'
        target_instances = self.get_target_instances()
        if target_instances:
            for item in target_instances:
                if item['State'] == 'healthy':
                    response = self.elb.deregister_targets(
                        TargetGroupArn = self.TargetGroupArn,
                        Targets=[
                            {
                                'Id': item['Id']
                            },
                        ]
                    )
                    valid = '200'
                    break
        else:
            return valid

        return valid
            
    def shrink_work_by_ratio(self, ratio):
        """
        shrink one instance into the self.TargetGroupArn
        :return: msg: str
        """
        pass

if __name__ == '__main__':
    awscli = AwsClient()
    #print('grow_worker_by_one {}'.format(awscli.grow_worker_by_one()))
    # print('get_tag_instances:{}'.format(awscli.get_tag_instances()))
    # print('get_target_instances:{}'.format(awscli.get_target_instances()))
    #print('get_idle_instances:{}'.format(awscli.get_idle_instances()))
    print('grow_worker_by_one:{}'.format(awscli.grow_worker_by_one()))
    #print('shrink_worker_by_one:{}'.format(awscli.shrink_work_by_one()))

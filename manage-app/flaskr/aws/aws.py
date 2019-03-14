import boto3
import json
from datetime import datetime, timedelta
from math import ceil
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
            n = len(response['Datapoints'])
            m = 60 // n
            for datapoint in response['Datapoints']:
                for i in range(m):
                    datapoints.append([
                        int(datapoint['Timestamp'].timestamp()*1000 + i*60*1000),
                        float(datapoint['Average'])
                    ])
            print(len(datapoints))
            return json.dumps(sorted(datapoints, key=lambda x: x[0]))
        else:
            return []

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
                 'Id': reservation['Instances'][0]['InstanceId'],
                 'State':reservation['Instances'][0]['State']['Name']
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
    
    def get_specfic_instance_state(self,instance_id):
        """
        describe specfic state of an instance 
        """
        response = self.ec2.describe_instance_status(InstanceIds = [instance_id,]) 
        # response['InstanceStatuses'][0]['InstanceState']['Name']
        return response

    def grow_worker_by_one(self):
        """
        add one instance into the self.TargetGroupArn
        :return: msg: str
        register_targets(**kwargs)
        """
        idle_instances = self.get_idle_instances()
        if idle_instances:
            first_idle_instance = idle_instances[0]
            # start instance
            self.ec2.start_instances(
                InstanceIds=[
                    first_idle_instance,
                ]
            )
            specfic_state = self.get_specfic_instance_state(first_idle_instance)
            while len(specfic_state['InstanceStatuses']) < 1:
                specfic_state = self.get_specfic_instance_state(first_idle_instance)
                
            while specfic_state['InstanceStatuses'][0]['InstanceState']['Name'] == 'pending':
                specfic_state = self.get_specfic_instance_state(first_idle_instance)
            # surveil if it has finished initializing
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
        idle_instances = self.get_idle_instances()
        target_instances = self.get_target_instances()
        register_targets_num =int(len((target_instances) * (ratio-1)))
        response_list = []
        if register_targets_num <= 0:
            return "Invalid ratio"
        if len(target_instances) < 1:
            return "You have no target instance in your group yet."
        if idle_instances:
            if len(idle_instances) < register_targets_num:
                #### to be changed to create and launch new instances
                return "Your instances exceed max number"
            else:
                for index in range(register_targets_num):
                    response_list.append(self.grow_worker_by_one())
       
        else:
            # here to create and launch new instances
            pass
        return response_list

    def shrink_work_by_one(self):
        """
        shrink one instance into the self.TargetGroupArn
        :return: msg: str
        """
        valid = '500'
        target_instances = self.get_target_instances()
        instance_to_be_stopped = ''
        if target_instances:
            for item in target_instances:
                if item['State'] == 'healthy':
                    #deregister instance from target group
                    response = self.elb.deregister_targets(
                        TargetGroupArn = self.TargetGroupArn,
                        Targets=[
                            {
                                'Id': item['Id']
                            },
                        ]
                    )
                    instance_to_be_stopped = item['Id']
                    #stop instance
                    response = self.ec2.stop_instances(
                        InstanceIds=[
                            instance_to_be_stopped,
                        ],
                        Hibernate=False,
                        Force=False
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
        target_instances = self.get_target_instances()
        response_list =[]
        if ratio < 1:
            return "Ratio should be more than 1"
        elif len(target_instances)<1 :
            return "Target instance group is already null"
        else:
            shrink_targets_num= i =len(target_instances) - ceil(len(target_instances) * round(1/ratio,2))
            for item in target_instances:
                response_list.append(self.shrink_work_by_one())
                i -= 1
                if i == 0:
                    break
        
        return response_list
                    

if __name__ == '__main__':
    awscli = AwsClient()
    #print('grow_worker_by_one {}'.format(awscli.grow_worker_by_one()))
    # print('get_tag_instances:{}'.format(awscli.get_tag_instances()))
    # print('get_target_instances:{}'.format(awscli.get_target_instances()))
    # print('get_idle_instances:{}'.format(awscli.get_idle_instances()))
    # print('grow_worker_by_one:{}'.format(awscli.grow_worker_by_one()))
    # print('shrink_worker_by_one:{}'.format(awscli.shrink_work_by_one()))
    # print('grow_worker_by_ratio:{}'.format(awscli.grow_worker_by_ratio(3)))
    print('shrink_worker_by_ratio:{}'.format(awscli.shrink_work_by_ratio(3)))
    # print('get_specfic_instance_state:{}'.format(awscli.get_specfic_instance_state('i-0c721ce50e7979880')))
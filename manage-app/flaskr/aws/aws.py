import boto3
import json
from math import ceil
import logging
from botocore.exceptions import ClientError
import time

class AwsClient:
    def __init__(self):
        self.ec2 = boto3.client('ec2')
        self.elb = boto3.client('elbv2')
        self.s3 = boto3.client('s3')
        self.bk = 'ece1779-images'
        self.TargetGroupArn = \
            'arn:aws:elasticloadbalancing:us-east-1:536627286469:targetgroup/target-group1/c0b38de79630ee69'
        self.cloudwatch = boto3.client('cloudwatch')
        self.user_app_tag = 'user-ece1779-a2'
        self.image_id = 'ami-07d04e8c9e62bf70c'
        self.instance_type ='t2.micro'
        self.keypair_name ='liuweilin17'
        self.security_group=['launch-wizard-2']
        self.tag_specification=[{
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': self.user_app_tag
                }]
        }]
        self.monitoring = {
            'Enabled': False
        }
        self.tag_placement ={
            'AvailabilityZone': 'us-east-1a'
        }

    def create_ec2_instance(self):
        try:
            response = self.ec2.run_instances(ImageId=self.image_id,
                                                InstanceType=self.instance_type,
                                                KeyName=self.keypair_name,
                                                MinCount=1,
                                                MaxCount=1,
                                                SecurityGroups=self.security_group,
                                                TagSpecifications=self.tag_specification,
                                                Monitoring = self.monitoring,
                                                Placement = self.tag_placement)
            return response['Instances'][0]

        except ClientError as e:
            logging.error(e)
            return None

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
                 'State': reservation['Instances'][0]['State']['Name']
                })
        return instances

    # if the instances in the target group are stopped, then the state is unused,
    # and the instances still stay in the target group.
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

    # when the state is draining, the instance is actually out of the target group
    def get_valid_target_instances(self):
        target_instances = self.get_target_instances()
        target_instances_id = []
        for item in target_instances:
            if item['State'] != 'draining':
                target_instances_id.append(item['Id'])
        return target_instances_id

    # we have to make instances in the target group are all running
    # in order to make sure that the idle instances are outside the target group.
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

    # cannot get the state of stopped instances
    def get_specfic_instance_state(self, instance_id):
        """
        describe specfic state of an instance 
        """
        response = self.ec2.describe_instance_status(InstanceIds=[instance_id])
        # response['InstanceStatuses'][0]['InstanceState']['Name']
        return response

    def grow_worker_by_one(self):
        """
        add one instance into the self.TargetGroupArn
        :return: msg: str
        register_targets(**kwargs)
        """
        idle_instances = self.get_idle_instances()

        new_instance_id = None
        if idle_instances:
            new_instance_id = idle_instances[0]
            # start instance
            self.ec2.start_instances(
                InstanceIds=[new_instance_id]
            )
        else:
            response = self.create_ec2_instance()
            new_instance_id = response['InstanceId']

        specfic_state = self.get_specfic_instance_state(new_instance_id)
        while len(specfic_state['InstanceStatuses']) < 1:
            time.sleep(1)
            specfic_state = self.get_specfic_instance_state(new_instance_id)

        while specfic_state['InstanceStatuses'][0]['InstanceState']['Name'] != 'running':
            time.sleep(1)
            specfic_state = self.get_specfic_instance_state(new_instance_id)

        # register if it has finished initializing
        response = self.elb.register_targets(
            TargetGroupArn = self.TargetGroupArn,
            Targets=[
                {
                    'Id': new_instance_id,
                    'Port': 5000
                },
            ]
        )

        if response and 'ResponseMetadata' in response and \
                'HTTPStatusCode' in response['ResponseMetadata']:
            return response['ResponseMetadata']['HTTPStatusCode']
        else:
            return -1

    def grow_worker_by_ratio(self, ratio):
        """
        add one instance into the self.TargetGroupArn
        :return: msg: str
        """
        target_instances = self.get_valid_target_instances()
        register_targets_num = int(len(target_instances) * (ratio-1))
        response_list = []
        if register_targets_num <= 0:
            return "Invalid ratio"
        if len(target_instances) < 1:
            return "You have no target instance in your group yet."

        for i in range(register_targets_num):
            response_list.append(self.grow_worker_by_one())
        return response_list

    def shrink_worker_by_one(self):
        """
        shrink one instance into the self.TargetGroupArn
        :return: msg: str
        """
        target_instances_id = self.get_valid_target_instances()
        flag, msg = True, ''
        if len(target_instances_id) > 1:
            unregister_instance_id = target_instances_id[0]

            # unregister instance from target group
            response1 = self.elb.deregister_targets(
                TargetGroupArn=self.TargetGroupArn,
                Targets=[
                    {
                        'Id': unregister_instance_id
                    },
                ]
            )
            status1 = -1
            if response1 and 'ResponseMetadata' in response1 and \
                    'HTTPStatusCode' in response1['ResponseMetadata']:
                status1 = response1['ResponseMetadata']['HTTPStatusCode']

            if int(status1) == 200:
                #stop instance
                status2 = -1
                response2 = self.ec2.stop_instances(
                    InstanceIds=[
                        unregister_instance_id,
                    ],
                    Hibernate=False,
                    Force=False
                )
                if response2 and 'ResponseMetadata' in response2 and \
                        'HTTPStatusCode' in response2['ResponseMetadata']:
                    status2 = response2['ResponseMetadata']['HTTPStatusCode']
                if int(status2) != 200:
                    flag = False
                    msg = "Unable to stop the unregistered instance"
            else:
                flag = False
                msg = "Unable to unregister from target group"

        else:
            flag = False
            msg = "No workers to unregister"

        return [flag, msg]
            
    def shrink_worker_by_ratio(self, ratio):
        """
        shrink one instance into the self.TargetGroupArn
        :return: msg: str
        """
        target_instances_id = self.get_valid_target_instances()
        response_list = []
        if ratio < 1:
            return [False, "Ratio should be more than 1", response_list]
        elif len(target_instances_id) < 1:
            return [False, "Target instance group is already null", response_list]
        else:
            shrink_targets_num = len(target_instances_id) - ceil(len(target_instances_id) * round(1/ratio, 2))
            for i in range(shrink_targets_num):
                response_list.append(self.shrink_worker_by_one())
        
        return [True, "Success", response_list]


    def get_cpu_utils(self, instance_id, start_time, end_time):
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
                    int(datapoint['Timestamp'].timestamp() * 1000),
                    float(datapoint['Maximum'])
                ])
            return json.dumps(sorted(datapoints, key=lambda x: x[0]))
        else:
            return json.dumps([[]])


    def clear_s3(self):
        self.s3.delete_objects(
            Bucket=self.bk,
            Delete={
                'Objects': [
                    {
                        'Key': '*',
                        #'VersionId': 'string'
                    },
                ],
                'Quiet': True
            },
            # MFA='string',
            # RequestPayer='requester',
            # BypassGovernanceRetention=True | False
        )

if __name__ == '__main__':
    awscli = AwsClient()
    # print('grow_worker_by_one {}'.format(awscli.grow_worker_by_one()))
    # print('get_tag_instances:{}'.format(awscli.get_tag_instances()))
    # print('get_target_instances:{}'.format(awscli.get_target_instances()))
    # print('get_idle_instances:{}'.format(awscli.get_idle_instances()))
    # print('grow_worker_by_one:{}'.format(awscli.grow_worker_by_one()))
    print('shrink_worker_by_one:{}'.format(awscli.shrink_worker_by_one()))
    # print('grow_worker_by_ratio:{}'.format(awscli.grow_worker_by_ratio(4)))
    # print('shrink_worker_by_ratio:{}'.format(awscli.shrink_worker_by_ratio(2)))
    # print('get_specfic_instance_state:{}'.format(awscli.get_specfic_instance_state('i-05d30395630a679bd')))
    # print('create_ec2_instances:{}'.format(awscli.create_ec2_instance()))
    
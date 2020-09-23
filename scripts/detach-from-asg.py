import json
import boto3


def lambda_handler(event, context):
    if isinstance(event, str):
        event = json.loads(event)

    client = assume_role(f"arn:aws:iam::{event['account_id']}:role/aws-controltower-AdministratorExecutionRole",
                         "demisto", 'autoscaling', event['region'])

    response = client.detach_instances(
        InstanceIds=[
            event['instance_id'],
        ],
        AutoScalingGroupName=event['asg_name'],
        ShouldDecrementDesiredCapacity=False
    )

    return {
        'statusCode': 200,
        'body': f"{event['instance_id']} has been removed from ASG {event['asg_name']}"
    }


def assume_role(arn, session_name, service, region):
    client = boto3.client('sts')

    response = client.assume_role(RoleArn=arn, RoleSessionName=session_name)

    session = boto3.Session(aws_access_key_id=response['Credentials']['AccessKeyId'],
                            aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                            aws_session_token=response['Credentials']['SessionToken'],
                            region_name=region)

    return session.client(service)
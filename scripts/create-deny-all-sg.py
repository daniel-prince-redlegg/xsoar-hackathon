import json
import boto3


def lambda_handler(event, context):
    if isinstance(event, str):
        event = json.loads(event)

    client = assume_role(f"arn:aws:iam::{event['account_id']}:role/aws-controltower-AdministratorExecutionRole",
                         "demisto", 'ec2', event['region'])

    response = client.create_security_group(
        GroupName='deny-all',
        Description='Deny-All',
        VpcId=event['vpc_id']
    )

    client.revoke_security_group_egress(
        GroupId=response['GroupId'],
        IpPermissions=[
            {
                'IpProtocol': '-1',
                'IpRanges': [
                    {
                        'CidrIp': '0.0.0.0/0',
                    },
                ]
            }
        ]
    )

    return {
        'statusCode': 200,
        'body': f"Deny-all created"
    }


def assume_role(arn, session_name, service, region):
    client = boto3.client('sts')

    response = client.assume_role(RoleArn=arn, RoleSessionName=session_name)

    session = boto3.Session(aws_access_key_id=response['Credentials']['AccessKeyId'],
                            aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                            aws_session_token=response['Credentials']['SessionToken'],
                            region_name=region)

    return session.client(service)
